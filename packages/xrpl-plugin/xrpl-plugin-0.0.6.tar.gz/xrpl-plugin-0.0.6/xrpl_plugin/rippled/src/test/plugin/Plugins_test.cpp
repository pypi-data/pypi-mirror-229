//------------------------------------------------------------------------------
/*
    This file is part of rippled: https://github.com/ripple/rippled
    Copyright (c) 2012-2017 Ripple Labs Inc.

    Permission to use, copy, modify, and/or distribute this software for any
    purpose  with  or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.

    THE  SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH  REGARD  TO  THIS  SOFTWARE  INCLUDING  ALL  IMPLIED  WARRANTIES  OF
    MERCHANTABILITY  AND  FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY  SPECIAL ,  DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER  RESULTING  FROM  LOSS  OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION  OF  CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
*/
//==============================================================================

#include <ripple/protocol/Feature.h>
#include <ripple/protocol/jss.h>
#include <test/jtx.h>
#include <test/jtx/TestHelpers.h>

namespace ripple {

namespace test {

class Plugins_test : public beast::unit_test::suite
{
    std::unique_ptr<Config>
    makeConfig(std::string pluginPath)
    {
        auto cfg = test::jtx::envconfig();
        cfg->PLUGINS.push_back(pluginPath);
        return cfg;
    }

    void
    testTransactorLoading()
    {
        testcase("Load Plugin Transactors");

        using namespace jtx;
        Account const alice{"alice"};

        // plugin that doesn't exist
        {
            try
            {
                // this should crash
                Env env{
                    *this,
                    makeConfig("libplugin_test_faketest.dylib"),
                    FeatureBitset{supported_amendments()}};
                BEAST_EXPECT(false);
            }
            catch (std::runtime_error)
            {
                BEAST_EXPECT(true);
            }
        }

        // valid plugin that exists
        {
            Env env{
                *this,
                makeConfig("libplugin_test_setregularkey.dylib"),
                FeatureBitset{supported_amendments()}};
            env.fund(XRP(5000), alice);
            BEAST_EXPECT(env.balance(alice) == XRP(5000));
            env.close();
        }

        // valid plugin with custom SType/SField
        {
            Env env{
                *this,
                makeConfig("libplugin_test_trustset.dylib"),
                FeatureBitset{supported_amendments()}};
            env.fund(XRP(5000), alice);
            BEAST_EXPECT(env.balance(alice) == XRP(5000));
            env.close();
        }

        // valid plugin with other features
        {
            Env env{
                *this,
                makeConfig("libplugin_test_escrowcreate.dylib"),
                FeatureBitset{supported_amendments()}};
            env.fund(XRP(5000), alice);
            BEAST_EXPECT(env.balance(alice) == XRP(5000));
            env.close();
        }
    }

    void
    testBasicTransactor()
    {
        testcase("Normal Plugin Transactor");

        using namespace jtx;
        Account const alice{"alice"};
        Account const bob{"bob"};

        Env env{
            *this,
            makeConfig("libplugin_test_setregularkey.dylib"),
            FeatureBitset{supported_amendments()}};
        env.fund(XRP(5000), alice);
        BEAST_EXPECT(env.balance(alice) == XRP(5000));

        // empty (but valid) transaction
        Json::Value jv;
        jv[jss::TransactionType] = "SetRegularKey2";
        jv[jss::Account] = to_string(alice.id());
        env(jv);

        // a transaction that actually sets the regular key of the account
        Json::Value jv2;
        jv2[jss::TransactionType] = "SetRegularKey2";
        jv2[jss::Account] = to_string(alice.id());
        jv2[sfRegularKey.jsonName] = to_string(bob.id());
        env(jv2);
        auto const accountRoot = env.le(alice);
        BEAST_EXPECT(
            accountRoot->isFieldPresent(sfRegularKey) &&
            (accountRoot->getAccountID(sfRegularKey) == bob.id()));

        env.close();
    }

    void
    run() override
    {
        using namespace test::jtx;
        testTransactorLoading();
        testBasicTransactor();
    }
};

BEAST_DEFINE_TESTSUITE(Plugins, plugins, ripple);

}  // namespace test
}  // namespace ripple

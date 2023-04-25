# -*- encoding: utf-8 -*-
"""
KERIA
keria.app.agenting module

Testing the Mark II Agent
"""
import json

import falcon
from falcon import testing
from keri.app import habbing, configing
from keri.app.keeping import Algos
from keri.core import coring, eventing, parsing
from keri.core.coring import MtrDex
from keri.peer import exchanging

from keria.app import aiding


def test_identifier_collection_end(helpers):
    caid = "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    salt = b'0123456789abcdef'
    salter = coring.Salter(raw=salt)
    cf = configing.Configer(name="keria", headDirPath="scripts", temp=True, reopen=True, clear=False)

    with helpers.openKeria(caid, salter, temp=True, cf=cf) as (agency, agent, app, client), \
            habbing.openHby(name="p1", temp=True) as p1hby, \
            habbing.openHby(name="p2", temp=True) as p2hby:

        end = aiding.IdentifierCollectionEnd()
        resend = aiding.IdentifierResourceEnd()
        app.add_route("/identifiers", end)
        app.add_route("/identifiers/{name}", resend)

        client = testing.TestClient(app)

        res = client.simulate_post(path="/identifiers", body=b'{}')
        assert res.status_code == 400
        assert res.json == {'description': "required field 'icp' missing from request",
                            'title': '400 Bad Request'}

        serder, signers = helpers.incept(salt, "signify:aid", pidx=0)
        assert len(signers) == 1
        signer0 = signers[0]
        diger0 = serder.digers[0]

        sigers = [signer.sign(ser=serder.raw, index=0).qb64 for signer in signers]

        body = {'name': 'aid1',
                'icp': serder.ked,
                'sigs': sigers,
                "salty": {
                    'stem': 'signify:aid', 'pidx': 0, 'tier': 'low',
                    'icodes': [MtrDex.Ed25519_Seed], 'ncodes': [MtrDex.Ed25519_Seed]}
                }

        res = client.simulate_post(path="/identifiers", body=json.dumps(body))
        assert res.status_code == 200

        res = client.simulate_get(path="/identifiers")
        assert res.status_code == 200
        assert res.json == [{'name': 'aid1',
                             'prefix': 'EHgwVwQT15OJvilVvW57HE4w0-GPs_Stj2OFoAHZSysY',
                             'salty': {'dcode': 'E',
                                       'icodes': ['A'],
                                       'kidx': 0,
                                       'ncodes': ['A'],
                                       'pidx': 0,
                                       'stem': 'signify:aid',
                                       'tier': 'low',
                                       'transferable': False}}]

        serder, signer = helpers.incept(salt, "signify:aid", pidx=1, count=3)
        sigers = [signer.sign(ser=serder.raw, index=0).qb64 for signer in signers]

        body = {'name': 'aid2',
                'icp': serder.ked,
                'sigs': sigers,
                'salty': {'stem': 'signify:aid', 'pidx': 1, 'tier': 'low',
                          'icodes': [MtrDex.Ed25519_Seed], 'ncodes': [MtrDex.Ed25519_Seed]}}
        res = client.simulate_post(path="/identifiers", body=json.dumps(body))
        assert res.status_code == 200

        res = client.simulate_get(path="/identifiers")
        assert res.status_code == 200
        assert len(res.json) == 2
        aid = res.json[0]
        assert aid["name"] == "aid1"
        assert aid["prefix"] == "EHgwVwQT15OJvilVvW57HE4w0-GPs_Stj2OFoAHZSysY"
        ss = aid[Algos.salty]
        assert ss["pidx"] == 0

        aid = res.json[1]
        assert aid["name"] == "aid2"
        assert aid["prefix"] == "ECL8abFVW_0RTZXFhiiA4rkRobNvjTfJ6t-T8UdBRV1e"
        ss = aid[Algos.salty]
        assert ss["pidx"] == 1

        # Test with witnesses
        serder, signers = helpers.incept(salt, "signify:aid", pidx=3,
                                         wits=["BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
                                               "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
                                               "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX", ],
                                         toad="2")
        sigers = [signer.sign(ser=serder.raw, index=0).qb64 for signer in signers]

        body = {'name': 'aid3',
                'icp': serder.ked,
                'sigs': sigers,
                'salty': {'stem': 'signify:aid', 'pidx': 3, 'tier': 'low',
                          'icodes': [MtrDex.Ed25519_Seed], 'ncodes': [MtrDex.Ed25519_Seed]}}

        res = client.simulate_post(path="/identifiers", body=json.dumps(body))
        assert res.status_code == 202

        assert len(agent.witners) == 1
        res = client.simulate_get(path="/identifiers")
        assert res.status_code == 200
        assert len(res.json) == 3
        aid = res.json[2]
        assert aid["name"] == "aid3"
        assert aid["prefix"] == serder.pre
        ss = aid[Algos.salty]
        assert ss["pidx"] == 3

        res = client.simulate_get(path=f"/identifiers/aid1")
        mhab = res.json
        agent0 = mhab["state"]

        # create member habs for group AID
        p1 = p1hby.makeHab(name="p1")
        assert p1.pre == "EBPtjiAY9ITdvScWFGeeCu3Pf6_CFFr57siQqffVt9Of"
        p2 = p2hby.makeHab(name="p2")
        assert p2.pre == "EMYBtOuBKVdp3KdW_QM__pi-UAWfrewlDyiqGcbIbopR"

        agentKvy = eventing.Kevery(db=agent.hby.db)
        psr = parsing.Parser(kvy=agentKvy)
        psr.parseOne(p1.makeOwnInception())
        psr.parseOne(p2.makeOwnInception())

        assert p1.pre in agent.hby.kevers
        assert p2.pre in agent.hby.kevers

        # Test Group Multisig
        keys = [signer0.verfer.qb64, p1.kever.verfers[0].qb64, p2.kever.verfers[0].qb64, ]
        ndigs = [diger0.qb64, p1.kever.digers[0].qb64, p2.kever.digers[0].qb64]

        serder = eventing.incept(keys=keys,
                                 isith="2",
                                 nsith="2",
                                 ndigs=ndigs,
                                 code=coring.MtrDex.Blake3_256,
                                 toad=0,
                                 wits=[])

        # Send in all signatures as if we are joining the inception event
        sigers = [signer0.sign(ser=serder.raw, index=0).qb64, p1.sign(ser=serder.raw, indices=[1])[0].qb64,
                  p2.sign(ser=serder.raw, indices=[2])[0].qb64]
        states = nstates = [agent0, p1.kever.state().ked, p2.kever.state().ked]
        body = {
            'name': 'multisig',
            'icp': serder.ked,
            'sigs': sigers,
            "smids": states,
            "rmids": nstates,
            'group': {
                "mhab": mhab,
                "keys": keys,
                "ndigs": ndigs
            }
        }

        res = client.simulate_post(path="/identifiers", body=json.dumps(body))
        assert res.status_code == 202

        res = client.simulate_get(path="/identifiers")
        assert res.status_code == 200
        assert len(res.json) == 4
        aid = res.json[3]
        assert aid["name"] == "multisig"
        assert aid["prefix"] == serder.pre
        assert aid["group"] == {'keys': ['DDNGgXzEO4LD8G1z1uD7eIDF2pDj6Y7hVx-nqhYZmU_8',
                                         'DAOF6DRwWDphP8F2r87uxTS9xwIehonmTBE1agJrPklA',
                                         'DPZ-k6HXUhiS5dPy8awuitFpwojGOQJ6DMZiatPjhXKC'],
                                'mhab': {'name': 'aid1',
                                         'prefix': 'EHgwVwQT15OJvilVvW57HE4w0-GPs_Stj2OFoAHZSysY',
                                         'salty': {'dcode': 'E',
                                                   'icodes': ['A'],
                                                   'kidx': 0,
                                                   'ncodes': ['A'],
                                                   'pidx': 0,
                                                   'stem': 'signify:aid',
                                                   'tier': 'low',
                                                   'transferable': False}},
                                'ndigs': ['EHj7rmVHVkQKqnfeer068PiYvYm-WFSTVZZpFGsClfT-',
                                          'ECTS-VsMzox2NoMaLIei9Gb6361Z3u0fFFWmjEjEeD64',
                                          'ED7Jk3MscDy8IHtb2k1k6cs0Oe5rEb3_8XKD1Ut_gCo8']}


def test_challenge_ends(helpers):
    caid = "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    salt = b'0123456789abcdef'
    salter = coring.Salter(raw=salt)
    cf = configing.Configer(name="keria", headDirPath="scripts", temp=True, reopen=True, clear=False)
    with helpers.openKeria(caid, salter, temp=True, cf=cf) as (agency, agent, app, client):
        end = aiding.IdentifierCollectionEnd()
        app.add_route("/identifiers", end)

        chaEnd = aiding.ChallengeEnd()
        app.add_route("/challenges", chaEnd)
        chaResEnd = aiding.ChallengeResourceEnd()
        app.add_route("/challenges/{name}", chaResEnd)

        client = testing.TestClient(app)

        result = client.simulate_get(path="/challenges?strength=256")
        assert result.status == falcon.HTTP_200
        assert "words" in result.json
        words = result.json["words"]
        assert len(words) == 24

        result = client.simulate_get(path="/challenges")
        assert result.status == falcon.HTTP_200
        assert "words" in result.json
        words = result.json["words"]
        assert len(words) == 12

        data = dict()
        b = json.dumps(data).encode("utf-8")
        result = client.simulate_post(path="/challenges/joe", body=b)
        assert result.status == falcon.HTTP_400  # Bad allias
        result = client.simulate_post(path="/challenges/pal", body=b)
        assert result.status == falcon.HTTP_400  # Missing words

        # Create an AID to test against
        aid = helpers.createAid(client, "pal", salt)

        payload = dict(i=aid['i'], words=words)
        exn = exchanging.exchange(route="/challenge/response", payload=payload)
        ims = agent.agentHab.endorse(serder=exn, last=True, pipelined=False)
        del ims[:exn.size]

        data["exn"] = exn.ked
        data["sig"] = ims.decode("utf-8")
        b = json.dumps(data).encode("utf-8")
        result = client.simulate_post(path="/challenges/pal", body=b)
        assert result.status == falcon.HTTP_400  # Missing recipient

        data["recipient"] = "Eo6MekLECO_ZprzHwfi7wG2ubOt2DWKZQcMZvTbenBNU"
        b = json.dumps(data).encode("utf-8")
        result = client.simulate_post(path="/challenges/pal", body=b)
        assert result.status == falcon.HTTP_202

        data = dict()
        data["aid"] = "Eo6MekLECO_ZprzHwfi7wG2ubOt2DWKZQcMZvTbenBNU"
        b = json.dumps(data).encode("utf-8")
        result = client.simulate_put(path="/challenges/henk", body=b)
        assert result.status == falcon.HTTP_400  # Missing recipient

        b = json.dumps(data).encode("utf-8")
        result = client.simulate_put(path="/challenges/pal", body=b)
        assert result.status == falcon.HTTP_400  # Missing said

        data["said"] = exn.said
        b = json.dumps(data).encode("utf-8")
        result = client.simulate_put(path="/challenges/pal", body=b)
        assert result.status == falcon.HTTP_202

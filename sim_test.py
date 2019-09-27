import datetime
import argparse
import imp
import os

import pandas as pd

from recogym import (
    competition_score,
    AgentInit
)

parser = argparse.ArgumentParser()
parser.add_argument('--P', type = int, default = 100, help = 'Number of products')
parser.add_argument('--U', type = int, default = 200, help = 'Number of users to train on')
parser.add_argument('--Utest', type = int, default = 2000, help = 'Number of users to test')
parser.add_argument('--seed', type = int, default = 42, help = 'Seed')
parser.add_argument('--K', type = int, default = 20, help = 'Number of latent factors')
parser.add_argument('--F', type = int, default = 50,
                    help = 'Number of flips, how different is bandit from organic')
parser.add_argument('--log_epsilon', type = float, default = 0.05,
                    help = 'Pop logging policy epsilon')
parser.add_argument('--sigma_omega', type = float, default = 0.01, help = 'sigma_omega')
parser.add_argument('--entries_dir', type = str, default = 'entries',
                    help = 'directory with agent .py files')

args = parser.parse_args()

P, U, Utest, seed, F, K, sigma_omega, log_epsilon, entries_dir = args.P, args.U, args.Utest, args.seed, args.F, args.K, args.sigma_omega, args.log_epsilon, args.entries_dir

print(args)

adf = []

for e in os.listdir(entries_dir):
    print(open(entries_dir + '/' + e).read())

    tmp_module = imp.new_module('tmp_module')
    tmp_module.__dict__['P']=P
    exec(open(entries_dir + '/' + e).read(), tmp_module.__dict__,)
    agent_key = list(tmp_module.agent.keys())[0]
    agent_data = tmp_module.agent[agent_key]
    df = competition_score(
        P,
        U,
        Utest,
        seed,
        K,
        F,
        log_epsilon,
        sigma_omega,
        agent_data[AgentInit.CTOR],
        agent_data[AgentInit.DEF_ARGS]
    )

    df = df.join(pd.DataFrame({
        'entry': [e.replace('.py', '')]
    }))

    print(df)

    adf.append(df)

out_dir = entries_dir + '_' + str(P) + '_' + str(U) + '_' + str(Utest) + '_' + str(datetime.datetime.now())
os.mkdir(out_dir)
fp = open(out_dir + '/config.txt', 'w')
fp.write(str(args))
fp.close()

leaderboard = pd.concat(adf)
leaderboard = leaderboard.sort_values(by = 'q0.500', ascending = False)
leaderboard.to_csv(out_dir + '/leaderboard.csv')

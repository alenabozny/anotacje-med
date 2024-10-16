import streamlit_authenticator as stauth
from random_word import RandomWords
from tqdm import tqdm
import yaml
import argparse

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--num-users", "-n", type=int, default=10)
parser.add_argument("--yaml-outfile", "-o", type=str, default="users.yaml")
parser.add_argument("--prefix", "-p", type=str, default="anotator")
parser.add_argument("--wordnum-pwd", "-w", type=int, default=3)
args = parser.parse_args()

def password_generator(wordnum=args.wordnum_pwd, separator="-"):
    rword = RandomWords()
    return separator.join([rword.get_random_word() for x in range(wordnum)])

USER_NUM = args.num_users
USERDICT = {}
PASSES = {}

for num in tqdm(range(USER_NUM)):
    _uname = f"{args.prefix}_{num}"
    _name = f"{args.prefix.upper()} #{num}"
    _pass = password_generator()
    _hashed = stauth.Hasher([_pass]).generate()

    PASSES[_uname] = _pass

    USERDICT[_uname] = {"email": "",
                        "name": _name,
                        "password": _hashed[0]}

# DANGEROUS; JUST FOR TESTING PURPOSES
# AND/OR TO DISTRIBUTE TO ANOTATORS
# DO NOT USE IN PRODUCTION

# with open(f"{args.yaml_outfile.replace(".","_")}_CREDS_PLAINTEXT_NOT_FOR_PRODUCTION.yaml", "w") as passout:
#     passout.write(yaml.dump(PASSES))
filename = args.yaml_outfile.replace(".","_")
with open(f"{filename}_CREDS_PLAINTEXT_NOT_FOR_PRODUCTION.yaml", "w") as passout:
    passout.write(yaml.dump(PASSES))

# # 
with open(args.yaml_outfile, "w") as usout:
    usout.write(yaml.dump(USERDICT))
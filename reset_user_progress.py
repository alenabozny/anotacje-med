import os, shutil

users = [x for x in os.listdir("data/replies/") if not x.startswith(".")]
fresh_to_touch = ["logs", "logs/general.txt", "finished", "packs_done.txt"]

for user in users:
    inside = os.listdir(os.path.join("data/replies/", user))
    for file in inside:
        try:
            file = f"'{file}'"
            os.system(f"rm -r {os.path.join('data/replies/', user, file)}")
        except:
            shutil.rmtree(os.path.join('data/replies/', user, file))

    for f in fresh_to_touch:
        if "." not in f:
            # it's a folder, create it
            os.mkdir(os.path.join('data/replies/', user, f))
        else:
            with open(os.path.join('data/replies/', user, f), "w") as fout:
                pass
import subprocess

def get_staged_diff()->str:
    result = subprocess.run(["git", "diff", "--staged"],capture_output=True,text=True,check=True)
    return result.stdout

def main():
    diff=get_staged_diff()
    if not diff.strip():
        print ("Nothing is staged")
        return
    print(diff)

if __name__=="__main__":
    main()
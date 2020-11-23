
import os, sys, getopt
import platform

options = ["help", "version", "build", "deploy", "get", "scale", "remove" ]
help_desciption1 = [
    "-h, --help",
    "-v, --verison",
    "-b, --build",
    "-d, --deploy",
    "-g, --get",
    "-s <pod count>, --scale <pod count>",
    "-r, --remove"
]
help_desciption2 = [
    "Desplay all options ",
    "Get script verion",
    "Build application and dockerizing",
    "Deploy all resource",
    "Get to desplay all resource",
    "Scale in or out for application",
    "Destory all resource"
]

Version = "0.1"

def viewHelp():
    print()
    print('Script Options')
    print('******************************************************************************************')
    print('%-10s   %-35s\t%s' % ("[cmd]", "[option]", "[description]"))
    for ops in options:
        print('%-10s : %-35s\t%s' % (ops, help_desciption1[options.index(ops)], help_desciption2[options.index(ops)] ))    
    print('******************************************************************************************')
    print()

def build():
    print('Start build application and dockerizing via gradle')
    if 'window' in platform.system():
        os.system('gradlew.bat dockerPush')
    else:
        os.system('gradlew dockerPush')

def deploy(arg):
    if arg == "all":
        print("Deploy all resource")
        os.system('kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/baremetal/deploy.yaml')
        os.system('kubectl apply -f ./k8s_manifest/')
    elif arg == "app":
        print("Deploy Application")
        os.system('kubectl apply -f ./k8s_manifest/deply_app.yaml')
    else:
        print("invalid sub argument!")

def getall():
    print("Get all k8s resource")
    os.system('kubectl get all -n default')
    print('get ingress information')
    os.system('kubectl -n ingress-nginx get svc ingress-nginx-controller')

def scale(arg):    
    print("Scale re-size : %d" % int(arg))

    if int(arg) > 0:
        pod_count = int(arg)
        os.system('kubectl scale deploy petclinic-deploy --replicas=%d' % pod_count)    
    else:
        print("invalid sub option. please check options -h")
        sys.exit(2)

def remove():
    print("remove all resource")
    os.system('kubectl delete svc petclinic-service')
    os.system('kubectl delete deploy petclinic-deploy')
    os.system('kubectl delete svc mysql')
    os.system('kubectl delete statefulsets mysql-stateful')
    os.system('kubectl delete statefulsets mysql-stateful')
    os.system('kubectl delete ingress test-ingress')

def main(argv):
    FILE_NAME = argv[0]
    print()
    print('Working path: ', os.getcwd())
    try:
        opts, etc_args = getopt.getopt(argv[1:], "hvbd:gs:r", options)
    except getopt.GetoptError: # invalid option
        print("invalid argument! Please check option.\n", FILE_NAME, " -help or -h" )
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            viewHelp()
            sys.exit()
        elif opt in ("-v", "--version"):
            print('\n******************* K8S Manager *******************\n', \
                    'version %s\n' % Version,\
                    '***************************************************\n'   )
            sys.exit()
        elif opt in ("-b", "--build"):
            build()
            sys.exit()
        elif opt in ("-d", "--deploy"):
            deploy(arg)
            sys.exit()
        elif opt in ("-g", "--get"):
            getall()
            sys.exit()
        elif opt in ("-s", "--scale"):
            scale(arg)
            sys.exit()
        elif opt in ("-r", "--remove"):
            remove()
            sys.exit()


if __name__ == "__main__":
    main(sys.argv)
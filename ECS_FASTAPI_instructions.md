# LOG PASOS DE:
# <https://www.beabetterdev.com/2023/01/29/ecs-fargate-tutorial-with-fastapi/>

## AWS - Docker

* Instrucciones Intalar AWS CLI https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
* verificar instalación
	> aws --version
* Instalar Docker (ver presentación clases para Linux o instalar Docker Desktop para Windows)

## ECR
* Armar estructura
```
src
├── app
│   ├── __init__.py
│   └── main.py
├── Dockerfile
└── requirements.txt
```
* crear AWS access key para user IAM en
<https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html>
```
matias
AKIATSHIYVETHIAL****
```
<BLRH>

  ```
4Wrww6Hl24XSPOorF4x6O8kr9dQm3MC04UXak5IZ
```
* dar permission policy: "AmazonEC2ContainerRegistryFullAccess"
* Configurar el AWS CLI. Si estás en Linux, de acá en adelante, poner "sudo" delante de cada vez que aparece el comando "aws" o "docker":
```
aws configure
```
* correr
```
aws ecr create-repository --repository-name repo_aws
```

* Copiar URI del ECR creado: ```2245301291302.dkr.ecr.us-east-1.amazonaws.com/repo_aws```
* seleccionar ECR y clickear: "view push commands". copiarlos

1. ``aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 245301291302.dkr.ecr.us-east-1.amazonaws.com```
2. ```docker build -t repo_aws .```
3. ```docker tag repo_aws:latest 245301291302.dkr.ecr.us-east-1.amazonaws.com/repo_aws:latest```
4. ```docker push 245301291302.dkr.ecr.us-east-1.amazonaws.com/repo_aws:latest```

* correr 
```docker build -t <repository URI>:latest .```
(este es una mezcla de 2 y 3)
* correr ```docker run 245301291302.dkr.ecr.us-east-1.amazonaws.com/repo_aws:latest```
(esto chequea que el contenedor anda bien localmente)
* correr comando 1
* correr comando 4. en ECR debería aparecer la imagen creada

## ECS

* Crear container en ECS. Todo default excepto activar "Use Container Insights".

* Panel izquierdo "Task definitions" luego "create new task definition". Todo default excepto:
    * name: app, 
    * URI: ver más arriba, 
    * puerto: mismo que corrida uvicorn del Dockerfile.
* Avanzar. 0.25 vCPU, .5GB
* Container size optional sí. Container "App". Mismas capacidades. crear ecsTaskExecutionRole. Instructivo: <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html> así aparece en las opciones de TaskRoles. Next. Crear
* En el nuevo task: deploy, run task.
* Elegir el cluster creado, Launch type, ponerle nombre al grupo.
* En Networking elegir el VPC asociado con tu cluster. Elegir un securiry group que tenga una inbound rule que acepte cualquier conexión http en el puerto 80. QUE PUBLIC IP ESTÉ ACTIVADO. Create.
* Entrar al Taskid y fijarse que el Last Status sea "running". Agarrar ahí el public IP y probar si funciona!











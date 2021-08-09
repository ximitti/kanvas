# Kanvas 📔
O Kanvas é uma API para cadastrar usuários (Instrutores, Facilitadores e Alunos), cadastrar cursos, atividades e submissões de alunos para essas atividades

Ao utilizar esta API, deve ser possível criar usuários, cadastrar cursos, atividades e submissões. Além do sistema de autenticação por tipo de usuário.

## Como instalar e rodar? 🚀
Para instalar o sistema, é necessário seguir alguns passos, como baixar o projeto e fazer instalação das dependências. Para isso, é necessário abrir uma aba do terminal e digitar o seguinte:

## Este passo é para baixar o projeto
git clone https://gitlab.com/ximitti/kanvas.git
Depois que terminar de baixar, é necessário entrar na pasta, criar um ambiente virtual e entrar nele:

## Entrar na pasta
	cd kanvas

## Criar um ambiente virtual

``` sh
    python3 -m venv venv

# Entrar no ambiente virtual:
    source venv/bin/activate

# Então, para instalar as dependências, basta:
    pip install -r requirements.txt

# Depois de ter instalado as dependências, é necessário rodar as migrations para que o banco de dados e as tabelas sejam criadas:
    ./manage.py migrate
    
# Então, para rodar, basta digitar o seguinte, no terminal:
    ./manage.py runserver
```
E o sistema estará rodando em http://127.0.0.1:8000/

## Utilização 🖥️
Para utilizar este sistema, é necessário utilizar um API Client, como o Insomnia

**Rotas**
**POST /api/accounts/**

Esta rota permite a criação dos usuários do sistema

Body:
``` json
// REQUEST
    {
    "username": "student",
    "password": "1234",
    "is_superuser": false,
    "is_staff": false
    }
```

Response:
``` json
// RESPONSE STATUS -> HTTP 201
    {
    "id": 1,
    "username": "student",
    "is_superuser": false,
    "is_staff": false
    }
```

Caso haja a tentativa de criação de um usuário que já está cadastrado o sistema deverá responder com HTTP 409 - Conflict.

**POST /api/login/**
fazendo login (serve para qualquer tipo de usuário)

Body:

``` json
// REQUEST
    {
    "username": "student",
    "password": "1234"
    }
```

Response:

``` json
// RESPONSE STATUS -> HTTP 200
    {
    "token": "dfd384673e9127213de6116ca33257ce4aa203cf"
    }
```
    
Esse token servirá para identificar o usuário em cada request. Na grande maioria dos endpoints seguintes, será necessário colocar essa informação nos Headers. O header específico para autenticação tem o formato Authorization: Token <colocar o token aqui>.

Caso haja a tentativa de login de uma conta que ainda não tenha sido criada, o sistema deverá retornar HTTP 401 - Unauthorized.

**POST /api/courses/**
Rota para criação de um curso
    
Body:

``` json
// REQUEST
// Header -> Authorization: Token <token-do-instrutor>
    {
    "name": "Node"
    }
```

    
Response:

``` json
// RESPONSE STATUS -> HTTP 201
    {
    "id": 1,
    "name": "Node",
    "users": []
    }
```
    
**PUT /api/courses/**<int:course_id>**/registrations/**
Rota para atualizar a lista de estudantes matriculados em um curso

Body:
``` json
// REQUEST
// Header -> Authorization: Token <token-do-instrutor>
    {
    "user_ids": [3, 4, 5]
    }
```

Response:
``` json
// RESPONSE STATUS -> HTTP 200
    {
    "id": 1,
    "name": "Node",
    "users": [
        {
        "id": 3,
        "username": "student1"
        },
        {
        "id": 4,
        "username": "student2"
        },
        {
        "id": 5,
        "username": "student3"
        }
    ]
    }
```
    
**GET /api/courses/**
Rota para obter a lista de cursos e alunos

Response:
``` json
// RESPONSE STATUS -> HTTP 200
    [
    {
        "id": 1,
        "name": "Node",
        "users": [
        {
            "id": 3,
            "username": "student1"
        }
        ]
    },
    {
        "id": 2,
        "name": "Django",
        "users": []
    },
    {
        "id": 3,
        "name": "React",
        "users": []
    }
    ]
```

**GET /api/courses/**<int:course_id>**/**
Rota para filtrar por id de curso

Response:

``` json
// RESPONSE STATUS -> HTTP 200
    {
    "id": 1,
    "name": "Node",
    "users": [
        {
        "id": 3,
        "username": "student1"
        }
    ]
    }
```

**DELETE /api/courses/**<int:course_id>**/**
Rota para deletar curso por id

``` json
// REQUEST
// Header -> Authorization: Token <token-do-instrutor>

// RESPONSE STATUS -> HTTP 204 NO CONTENT
```

**POST /api/activities/**
Rota para criar atividades

Body:

``` json
// REQUEST
// Header -> Authorization: Token <token-do-facilitador ou token-do-instrutor>
    {
    "title": "Kenzie Pet",
    "points": 10
    }
 
```

Response:

``` json
// RESPONSE STATUS -> HTTP 201
    {
    "id": 1,
    "title": "Kenzie Pet",
    "points": 10,
    "submissions": []
    }
```

**GET /api/activities/**
Rota para listar atividades

Request:

``` json
// REQUEST
// Header -> Authorization: Token <token-do-instrutor ou token-do-facilitador>
```

Response:

``` json
// RESPONSE STATUS -> HTTP 200
    [
    {
        "id": 1,
        "title": "Kenzie Pet",
        "points": 10,
        "submissions": [
        {
            "id": 1,
            "grade": 10,
            "repo": "http://gitlab.com/kenzie_pet",
            "user_id": 3,
            "activity_id": 1
        }
        ]
    },
    {
        "id": 2,
        "title": "Kanvas",
        "points": 10,
        "submissions": [
        {
            "id": 2,
            "grade": 8,
            "repo": "http://gitlab.com/kanvas",
            "user_id": 4,
            "activity_id": 2
        }
        ]
    },
    {
        "id": 3,
        "title": "KMDb",
        "points": 9,
        "submissions": [
        {
            "id": 3,
            "grade": 4,
            "repo": "http://gitlab.com/kmdb",
            "user_id": 5,
            "activity_id": 3
        }
        ]
    }
    ]
```

**POST /api/activities/**<int:activity_id>**/submissions/**
Rota para cadastrar submissões de atividades, somente estudantes podem fazer submissões

Body:

``` json
// REQUEST
// Header -> Authorization: Token <token-do-estudante>
    {
    "grade": 10, // Esse campo é opcional
    "repo": "http://gitlab.com/kenzie_pet"
    }
```

Response:

``` json
// RESPONSE STATUS -> HTTP 201
    {
    "id": 7,
    "grade": null,
    "repo": "http://gitlab.com/kenzie_pet",
    "user_id": 3,
    "activity_id": 1
    }
```

**PUT /api/submissions/**<int:submission_id>**/**
Rota para atualizar nota de submissão, somente instrutores e facilitadores tem permissão

Body:

``` json
// REQUEST
// Header -> Authorization: Token <token-do-facilitador ou token-do-instrutor>
    {
    "grade": 10
    }
```

Response:

``` json
// RESPONSE STATUS -> HTTP 200
    {
    "id": 3,
    "grade": 10,
    "repo": "http://gitlab.com/kenzie_pet",
    "user_id": 3,
    "activity_id": 1
    }
```

**GET /api/submissions/**
Rota para listar submissões, caso a autenticação seja de um aluno serão mostrados somente deste aluno, caso contrário serão listados todas as submissões

``` json
//REQUEST
//Header -> Authorization: Token <token-do-estudante>

// RESPONSE STATUS -> HTTP 200
    [
    {
        "id": 2,
        "grade": 8,
        "repo": "http://gitlab.com/kanvas",
        "user_id": 4,
        "activity_id": 2
    },
    {
        "id": 5,
        "grade": null,
        "repo": "http://gitlab.com/kmdb2",
        "user_id": 4,
        "activity_id": 1
    }
    ]
```

``` json
//REQUEST
//Header -> Authorization: Token <token-do-facilitador ou token-do-instrutor>

// RESPONSE STATUS -> HTTP 200
    [
    {
        "id": 1,
        "grade": 10,
        "repo": "http://gitlab.com/kenzie_pet",
        "user_id": 3,
        "activity_id": 1
    },
    {
        "id": 2,
        "grade": 8,
        "repo": "http://gitlab.com/kanvas",
        "user_id": 4,
        "activity_id": 2
    },
    {
        "id": 3,
        "grade": 4,
        "repo": "http://gitlab.com/kmdb",
        "user_id": 5,
        "activity_id": 3
    },
    {
        "id": 4,
        "grade": null,
        "repo": "http://gitlab.com/kmdb2",
        "user_id": 5,
        "activity_id": 3
    }
    ]
```



## Tecnologias utilizadas 📱
* Django
* Django Token Authentication
* Django Rest Framework
* SQLite
___________________________________________
### Licence
MIT

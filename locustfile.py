from string import ascii_letters
import random

from locust import (HttpUser,
                    task,
                    between,
                    run_single_user)

class AuthTest(HttpUser):
    host = 'https://auth-pet-grisha-3108.amvera.io'
    wait_time = between(1, 5)

    def on_start(self):
        username_length = random.randint(1, 30)
        username_charlist = random.choices(ascii_letters, k=username_length)
        self.username = ''.join(username_charlist) + '@mail.ru'
        with self.client.post('/auth/register', 
                         json={'username': self.username, 
                               'password': '11223344'},
                               catch_response=True,
                               timeout=10) as response:
            if response.json().get('username') != self.username:
                response.failure(f'Ошибка при регистрации пользователей, ответ:{response.json()}, а пользователь:{self.username}')
        with self.client.post('/auth/login', data={'grant_type': 'password',
                                                   'username': self.username,
                                                   'password': '11223344'}, 
                                                   catch_response=True,
                                                    timeout=10) as response:
            if response.json().get('token_type') not in ('Bearer', 'bearer'):
                response.failure('Ошибка при входе')
            else:
                self.authorization_header = 'Bearer ' + response.json().get('access_token')

    @task
    def get_user(self):
        with self.client.get('/auth/me', 
                       headers={'Authorization': self.authorization_header},
                       catch_response=True,
                       timeout=10) as response:
            if response.json().get('username') != self.username:
                response.failure(f'Ошибка при получении текущего пользователя. Ответ {response.json()}, а пользователь {self.username}')

    def on_stop(self):
        self.client.post('/auth/logout', headers={'Authorization': self.authorization_header}, timeout=10)


if __name__ == '__main__':
    run_single_user(AuthTest)
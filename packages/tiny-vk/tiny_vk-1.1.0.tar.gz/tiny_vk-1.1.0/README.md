# <img src="https://i.imgur.com/3zeCXQy.gif" width="250" height="" />

Tiny VK - это модуль, предназначенный для создания простых ботов для социальной сети ВКонтакте на ***Python 3.10 и выше***. Модуль основан на библиотеке [vk_api](https://github.com/python273/vk_api) и sqlite3.
#
## Установка
**GitHub**
```
pip install git+https://github.com/QuoNaro/tiny-vk.git
```
**PyPi**
```
pip install tiny-vk
```
#
## **Эхо-бот**

```python
from tiny_vk import Bot
bot = Bot(token)

@bot.on.message()
def echo(self):
  bot.utils.user_message(self.text)

bot.start()
```
# <img src="https://i.imgur.com/j9hag5e.gif"/>

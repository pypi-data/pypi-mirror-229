# camunda-adapter

Пакет предоставляет адаптер к платформе Camunda для приложений на Python.

## Установка

```bash

  $ pip install camunda-adapter

```


## Подключение и настройка


См. тестовое приложение src/testapp.


### apps.py:

Инстанцируется Config с параметрами конфигурации, затем инстанцируется Adapter.

При необходимости работы с внешними задачами, регистрируются обработчики задач путем подписки на соответствующие топики задач.



```python

from django.apps import AppConfig as AppConfigBase

from camunda_adapter.adapters import Adapter
from camunda_adapter.config import Config


class AppConfig(AppConfigBase):

    name = __package__

    def ready(self):
        self._setup_bpmn()

    def _setup_bpmn(self):
        from testapp import core

        from . import services

        core.config = Config()
        core.adapter = Adapter(core.config)

        for topic, handler in (
            (services.topic1, services.topic_handler1),
            (services.topic2, services.topic_handler2),
            (services.topicN, services.topic_handlerN),

        ):
            core.adapter.register_topic_handler(topic, handler)

```


### services.py:


```python

from camunda_adapter.domain import model as camunda


topic1 = camunda.Topic(name='topic-1')
def topic_handler1(task: camunda.ExternalTask, adapter: Adapter):
    ...


topic2 = camunda.Topic(name='topic-2')
def topic_handler2(task: camunda.ExternalTask, adapter: Adapter):
    ...


topicN = camunda.Topic(name='topic-N')
def topic_handlerN(task: camunda.ExternalTask, adapter: Adapter):
    ...

```

### Примеры непосредственного обращения к адаптеру:

Отправка сообщения:

```python

message = model.Message(
    messageName='DeclarationReceived',
    businessKey=f'attestation-declaration-{declaration.id}',
    processVariables={
        name: model.Variable(value=value)
        for name, value in declaration.dict(include={'id'}).items()
    }
)
message_results: List[model.MessageResult] = list(adapter.message(message))

```

Получение списка доступных задач:

```python

adapter.get_external_tasks(definition=definition)

```

Выполнение доступных задач:

```python

adapter.process_external_tasks()

```


## Тестирование

Для запуска тестов используется tox с плагином tox-docker, запускающим контейнер Camunda.

Установка tox:

```bash

$ pip install tox tox-docker

```

Запуск тестов из директории пакета:

```bash

$ tox

```

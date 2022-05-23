# Программное средстово для замены фона на изображении высокого разрешения в реальном времени

Программное средство позволяет осуществлять замену фона (матирование) на изображении в высоком разрешении и в режиме реального времени. Приложение имеет удобный интерфейс, который позволяет настраивать изображение и режимы функционирования алгоритма.

## Установка
В данном разделе описан процесс развёртывания и использования приложения, разрабатываемого в данном дипломном проекте, а также необходимые программно-аппаратные требования к системе для корректной работы программы.

### Установка клиентской части

Установка клиентской части приложения производится путём запуска файла MattingApp.apk на мобильном устройстве под управлением операционной системы Android.

Минимальные программно-аппаратные требования к установке:

    1.	Android версии 8.0 и выше
    2.	100 МБ оперативной памяти
    3.	Наличие камеры с поддержкой записи видео в разрешении не ниже 1280x720

### Установка серверной части

Минимальные программно-аппаратные требования к установке:

    1.	Операционная система Linux
    2.	Docker версии не ниже 20.0.0
    3.	Процессор Intel Xeon (или совместимый)
    4.	Видеокарта Nvidia K80
    5.	5 ГБ свободной памяти на диске
    6.	500 МБ оперативной памяти
    7.	Сетевая карта

Для установки серверной части приложения необходимо запустить файл BackgroundMatting_server.exe. Далее необходимо указать путь установки серверной части приложения. После успешной установки в выбранной директории появится следующий набор серверных файлов, необходимых для развёртывания:

    1.	Dockerfile – файл, необходимый для создания Docker-контейнера для развёртывания приложения
    2.	.dockerignore – включает в себя список файлов, которые не являются необходимыми для работы сервера, но нужны для первичной инициализации сервера
    3.	Папка scripts
    3.1.	build.sh
    3.2.	run.sh
    4.	Папка torchserve
    4.1.	resnet50.pth
    4.2.	config.properties
    4.3.	handler.py

Развёртывание серверной части приложения может осуществляться как на локальном компьютере, так и на удалённом сервере. Для этого в комплекте программы поставляется набор скриптов (папка scripts). Для создания контейнера docker используется скрипт build.sh.

Далее, данный контейнер может быть загружен на удалённый репозиторий контейнеров и напрямую использоваться на облачной платформе. Для запуска сервера на устройстве предназначен скрипт run.sh. После успешного запуска контейнера начинается процесс инициализации сервера. По окончанию инициализации сервер начинает вывод логовых сообщений, что свидетельствует о готовности к работе.
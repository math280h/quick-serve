# quick-serve
[![math280h](https://circleci.com/gh/math280h/quick-serve/tree/master.svg?style=svg)](https://app.circleci.com/pipelines/github/math280h/quick-serve)

A very simple and limited HTTP Server.

## Running
To run quick-serve simply run the following commands
```commandline
pip3 install -r requirements.txt
```

Then run:
```commandline
python3 run.py
```

## Configuration
quick-serve has two different config files, on for defining log configuration known as `log_config.ini` and one for defining all other configurations known as `config.ini`

### Configuration Parameters
#### config.ini
* General
    * ExtendedLogging
        * Bool - Default: false - If true the logging level is changed to `DEBUG`
    * WorkingDirectory
        * Path - Default: /var/www - This specifies the directory quick-serve should `work` in, e.g. where the resources is located
* Server
    * ListenAddress
        * IP Address - Default: 127.0.0.1 - This specifies the address the server should listen for requests on
    * Port
        * Port - Default: 80 - This specifies the port quick-serve should listen on
    * HttpVersion
        * HTTP Version - Default: 1.0 - This specifies which version of HTTP the server itself uses and includes in responses
    * ByteReadSize
        * Buffer Read Size - Default: 8192 - This specifies how many bytes the buffer should read at a time.
    * DefaultFile
        * Path - Default: /index.html - This specifies the file quick-serve should refer to if the requested resource is e.g. `/`
    * SupportedMethods[]
        * Array of HTTP Methods - Default: GET, PUT, HEAD, POST, DELETE, OPTIONS - This specifies what HTTP Methods is supported by quick-serve
    * DefaultEncoding
        * Encoding - Default UTF-8 - This specifies the encoding to use if none is specified in request headers
#### log_config.ini
This log contains configuration used by the `logger` package from python3, documentation on this config can be found here [here](https://docs.python.org/3/howto/logging.html#configuring-logging)

## Perfomance
quick-serve uses `asyncio` to handle many requests, once a connection is accepted it's moved into it's own task.

````
Requests per second:    9270.46 [#/sec] (mean)
Time per request:       32.361 [ms] (mean)
Time per request:       0.108 [ms] (mean, across all concurrent requests)
Transfer rate:          371.97 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0   10   2.1     10      27
Processing:     2   21  16.0     10      54
Waiting:        0   12  17.1      0      45
Total:          4   32  16.3     21      72

Percentage of the requests served within a certain time (ms)
  50%     21
  66%     48
  75%     52
  80%     53
  90%     55
  95%     57
  98%     58
  99%     59
 100%     72 (longest request)
````

## Testing
To run the unit tests you will first have to install requirements from the `dev-requirements.txt` file. This can be done using the following command:
```commandline
pip3 install -r dev-requirements.txt
```

First make sure that the server is running locally on `127.0.0.1:80` then you can follow the below guide to run the tests.

All tests are located `tests` and can be run by using the following command inside the directory:
```commandline
python -m unittest discover tests
```

### Current tests
* Connection
    * test_connection
        * Test that we can successfully connect to the server
    * test_headers
        * Test that we get the correct headers when requesting OPTIONS 
* Get
    * test_get_content
        * Test that we get content back when requesting default file
    * test_secure_path
        * Test that we cannot access paths outside of the working directory
* Resource
    * test_content_type
        * Test that we send the expected content_type for the given resource.
    * test_content_length
        * Test that we send the expected content_length for the given resource.

## Other
A big thanks to Kibb#4205 for starting this challenge on [TPH](https://theprogrammershangout.com/resources/projects/http-project-guide/intro.md)

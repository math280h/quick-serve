# quick-serve
[![math280h](https://circleci.com/gh/math280h/quick-serve/tree/master.svg?style=svg)](https://app.circleci.com/pipelines/github/math280h/quick-serve)

A very simple and limited HTTP Server.

## Running
quick-serve does not have any external dependency's for running in production other than `python3` and therefore all you have to do is run the `server.py` file located in the `src` directory.

## Configuration
quick-serve has two different config files, on for defining log configuration known as `log_config.ini` and one for defining all other configurations known as `config.ini`

### Configuration Parameters
#### config.ini
* General
    * ExtendedLogging
        * Bool - Default: false - This specifies if quick-serve should print everything it's logging or just the minimal
    * WorkingDirectory
        * Path - Default: /var/www - This specifies the directory quick-serve should `work` in, e.g. where the resources is located
* Server
    * ListenAddress
        * IP Address - Default: 127.0.0.1 - This specifies the address the server should listen for requests on
    * Port
        * Port - Default: 80 - This specifies the port quick-serve should listen on
    * HttpVersion
        * HTTP Version - Default: 1.1 - This specifies which version of HTTP the server itself uses and includes in responses
    * DefaultFile
        * Path - Default: /index.html - This specifies the file quick-serve should refer to if the requested resource is e.g. `/`
    * SupportedMethods[]
        * Array of HTTP Methods - Default: GET, PUT, HEAD, POST, DELETE, OPTIONS - This specifies what HTTP Methods is supported by quick-serve
#### log_config.ini
This log contains configuration used by the `logger` package from python3, documentation on this config can be found here [here](https://docs.python.org/3/howto/logging.html#configuring-logging)

## Perfomance
quick-serve uses Threading to handle many requests, once a connection is accepted it's moved into it's own thread.

````
Concurrency Level:      10
Time taken for tests:   0.259 seconds
Complete requests:      500
Failed requests:        0
Total transferred:      40000 bytes
HTML transferred:       0 bytes
Requests per second:    1928.80 [#/sec] (mean)
Time per request:       5.185 [ms] (mean)
Time per request:       0.518 [ms] (mean, across all concurrent requests)
Transfer rate:          150.69 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       1
Processing:     1    5   2.2      4      11
Waiting:        1    4   2.1      4      10
Total:          2    5   2.1      4      12

Percentage of the requests served within a certain time (ms)
  50%      4
  66%      5
  75%      7
  80%      7
  90%      9
  95%      9
  98%     10
  99%     10
 100%     12 (longest request)
````

## Testing
To run the unit tests you will first have to install requirements from the `dev-requirements.txt` file. This can be done using the following command:
```commandline
pip3 install -r dev-requirements.txt
```

First make sure that the server is running locally on `127.0.0.1:80` then you can follow the below guide to run the tests.

All tests are located `src/tests` and can be run by using the following command inside the directory:
```commandline
python -m unittest discover
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
Haystack
========

## Usage

```sh
# Start the indxer
sudo ./bin/haystack {start|stop|restart|status}

# Start the static file server
sudo ./bin/haystack-server {start|stop|restart|status}
```

## Setup

* `install.sh` will prepare the Raspberry Pi to run haystack.
* Make sure the values in `config.properties` and `lighttpd.conf` are correct.

## Development Notes

* Lint in Sublime Text 3 with `SublimeLinter-pep8`.

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

## TODOs

* Some .MTS videos aren't getting converted properly. :( In one example, (perhaps others)
the video gets scaled and there is a green bar on the right side???
* The transfer should ignore unrecognized files, like .DS_Store


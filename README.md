# Bam!

Bam is like [Pow][pow], but for [Django][django] and friends.  
Check it out, but ~~probably~~ don't use it ~~yet~~.

# Unmaintained :skull:

This tool has been broken for some years. It remains available as a historical
curiosity. Pull requests to fix it are welcome.

## Installation

1. Bam currently depends on [Dnsmasq][masq].  
   Installing and configuring it is simple:

   ```
   $ brew install dnsmasq
   $ echo "listen-address=127.0.0.1" >> /usr/local/etc/dnsmasq.conf
   $ echo "address=/bam/127.0.0.1" >> /usr/local/etc/dnsmasq.conf
   $ sudo cp /usr/local/Cellar/dnsmasq/2.61/homebrew.mxcl.dnsmasq.plist /Library/LaunchDaemons
   $ sudo launchctl load -w /Library/LaunchDaemons/homebrew.mxcl.dnsmasq.plist
   ```

2. Forward port 80 to Bam:

   ```
   $ ipfw add fwd 127.0.0.1,30559 tcp from any to me dst-port 80 in
   $ sysctl -w net.inet.ip.forwarding=1
   ```

3. Clone Bam via GitHub for now. It's not on PyPi yet.  
   You'll probably want to create a [virtualenv][venv] first.

   ```
   $ git clone git://github.com/adammck/bam.git
   $ cd bam
   $ ./bam.py
   ```

   That's it. There's no fancy launch script yet. I know, I know.


## Usage

Once you're up and running, adding an app is easy.  
Symlink it into `~/.bam`, and Bam takes care of the rest:

```
$ cd ~/.bam
$ ln -s /path/to/myapp
```

Your app is now available at **`http://myapp.bam`**.

### Virtualenv

To launch an app in a virtualenv, create a file named `.venv` containing the
path to the virtualenv in the project root. For example:

```
~/.virtualenv/myapp
```

### Environment Variables

To configure the environment in which an app is launched, create a file named
`.bam-vars` containing one variable per line in the `NAME=VALUE` format in the
project root. For example:

```
SECRET_KEY=aaaaaa
TWITTER_CONSUMER_KEY=bbbbbb
TWITTER_CONSUMER_SECRET=cccccc
```


## License

[Bam][repo] is free software, available under the [MIT license][license]




[repo]:    https://github.com/adammck/bam
[license]: https://raw.github.com/adammck/bam/master/LICENSE
[pow]:     http://pow.cx
[django]:  https://www.djangoproject.com
[masq]:    http://www.thekelleys.org.uk/dnsmasq/doc.html
[venv]:    http://www.virtualenv.org

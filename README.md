# sd<sup>2</sup>: Software Defined Software Development™
The Software Defined Software Development Process aka sd<sup>2</sup> is 
a modern Software Development approach that aims to simplify the 
complexity that usually accompanies working with multiple projects 
each with multiple branches and potentially each with its own
stack. sd<sup>2</sup> relies heavily on a **single** text 
file that describes a developer's development environments and in containers 
that isolate the different environments. sd<sup>2</sup> seperates the editing 
environment from the environment where compilation and testing takes place. 
In some sense, we bring the advantages of a microservices environment to 
the development phase even when you do not use microservices in production.

![Use Case](https://docs.google.com/drawings/d/1uO3umvqVMIM2HnrXJwRAgAX2UWRYNVqEKDTNggXlEIc/pub?w=960&h=720)

## Prerequisites
The tools have been tested on MacOS and Ubuntu hosts. At a minimum you 
need one machine (e.g. a MacOS notebook) with docker installed that will
 play the role of both the editing and the development machine.

1. Editing Host Requirements
   1. Python 2.7 with additional packages: python_hosts,jinja2,pyyaml
   1. fswatch (see [here](http://stackoverflow.com/questions/1515730/is-there-a-command-like-watch-or-inotifywait-on-the-mac))
   1. Add your user to sudoers (see [here](https://askubuntu.com/questions/168461/how-do-i-sudo-without-having-to-enter-my-password))
1. Development Host(s) Requirements
   1. Python 2.7 with additional packages: python_hosts,jinja2,pyyaml
   1. Add your user to sudoers (see [here](https://askubuntu.com/questions/168461/how-do-i-sudo-without-having-to-enter-my-password))
   1. ssh server
1. Other
   1. Before you start you need to make sure that you can use ssh with certificates to login from the editing machine to the development host(s). Do not add the hosts to .ssh/config or /etc/hosts.
   
## How to set it up
sd2 relies on a configuration file that defines your hosts, your conainers/images and your repositories. The configuration file should be in your home directory under .sd2 (ie ~/.sd2/config.yaml). A daemon called sd2d reads the configuration file and takes all the actions needed to maintain the connections and replicate the repositories in real time as they change in the development machine.

## What is not covered by sd<sup>2</sup>

1. Bring your own editor/IDE. We are agnostic how you edit your source code.
1. Bring your own container images. We do not provide tools to generate
 docker images, we expect that are already available and published in 
 a local or remote repository.
 
 ## FAQ
 1. When I run docker directly on the MacOS why can't I just mount the MacOS file system on the container?  
 This will work but in most cases, it will have sever performance implications. You ca read more about the issue [here](https://forums.docker.com/t/file-access-in-mounted-volumes-extremely-slow-cpu-bound/8076/174).
 1. Is sd2 secure when the development host is across the internet?  
 sd2 always uses ssh to communicate from the editing machine to the development machine so it is as secure as ssh itself.

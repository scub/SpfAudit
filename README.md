Auditing The Collective SPF Implementation
==========================================

  Google has developed some amazing services across the field of information
technology, and the integration of their services into consumer infrastructure
is getting easier and easier. However, because that ease of integration lends
itself so well to the average consumer, it no longer has the intimidation
factor that keeps most novice administrators from attempting to implement it
on their own production environments. The scope of my project will largely be
limited to Google's MX Services for small business.

  In order to use Google's mail exchanges, an administrator just has to add
googles SMTP relays in MX records for his or her domain's DNS. While this is a
straightforward way to integrate Google mail for a small business, it makes it
easy for an administrator to forget about security, which after all, is an
ever important concern within information technology. It is worth noting that
Google offered these services to the general public free of charge, during a
lengthy a beta phase.

  Because smtp requires no authentication, when mail exchanges and their
corresponding DNS records are not appropriately locked down, any user can
essentially spoof their mail to look as though it had been sent using these
exchanges without any type of verification required. My project will involve
creating an application that will search for these misconfigured exchanges,
then generate and send an email to the administrator of the domain with
instructions as to how they can better secure their exchanges.

  The end goal of this project would be to help the overall hardening of the
exchanges, ensuring a safer internet for everyone in contact with these
systems, while allowing statistics to be collected and documented;
metadata isn't just for the NSA, my friends!

  The proposed networked application will be built in python/ipython and
take place largely on the cloud within Amazon's brilliant EC2 infrastructure.
The services of various commonly used daemons will be harnessed within the
application which include but are certainly not limited to postgresql to help
with normalization and organization of data in concert with elasticsearch,
which when paired with an open source analytics engine such as kibana provides
an ample backend for real-time analytics.

  The dataset that will be used is the recently compiled DNS Census, which
was released to the public back in 2013. While the original set in its entirety
is around 2.7 billion records, through normalization techniques and specific 
targeting the number of hosts requiring processing was reduced dramatically.

- <a href="http://dnscensus2013.neocities.org/statistics.html">DNS Census 2013</a>
 
Recreate the results
--------------------

First we clone a copy of the spfAudit.git repo by running
```bash
git clone https://github.com/scub/spfAudit.git spf.aud.it && cd $_
```

  Now we go ahead and create our production node, with all required 
dependencies installed and services configured for us. 
```bash
vagrant up --provision-with puppet && vagrant reload && vagrant provision
```

  Once the machine has been provisioned we are ready to start scanning,
all that is required is to shell into the virtual machine and begin.
```bash
vagrant ssh
```

 After entering the nodes you wish to audit, all that is left is to kick 
on a browser and watch the data aggregate
```bash
http://localhost:8080
```

Upcoming Changes/Events
-----------------------
 - Connection Polling for scan initialization and sanity checks
 - Extend Vagrantfile to allow for cloud based deployment
 - "The Big Run"


Example Run State
-----------------
- Main Menu
<img src='http://i.imgur.com/pAhQO1i.jpg'/>

- Accepting Input
<img src='http://i.imgur.com/sw8aa9p.jpg'/>

- Puppet Run
<img src='http://i.imgur.com/gzTneUk.jpg'/>

- Broker Menus
<img src='http://i.imgur.com/bXfvkIX.jpg'/>

- Kibana/Nginx Stats Tracking
<img src='http://i.imgur.com/vwWYSWn.jpg'/>

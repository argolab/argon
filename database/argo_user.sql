DROP TABLE IF EXISTS `argo_user`;
CREATE TABLE IF NOT EXISTS `argo_user` (
    `uid` int(11) unsigned NOT NULL auto_increment,
    `userid` varchar(20) NOT NULL,
    `passwd` varchar(60),
    `username` varchar(20),
    `email` varchar(64) ,

    `remail` varchar(64),
    `netid`  varchar(64),

    `iconidx` varchar(32),

    `bgidx` varchar(32),

    -- `register` datetime NOT NULL default CURRENT_TIMESTAMP,
    -- `registerhost` varchar(20),
    `firstlogin` datetime NOT NULL default '1970-01-01 00:00:00',
    `firsthost` varchar(20),
    `lastlogin` datetime NOT NULL default '1970-01-01 00:00:00',
    `lasthost` varchar(20),
    `lastlogout` datetime NOT NULL default '1970-01-01 00:00:00',

    `numlogins` int(11) unsigned default 0,
    `numposts` int(11) unsigned default 0,
    `credit` int(11) unsigned default 0,
    `lastpost` datetime NOT NULL default '1970-01-01 00:00:00',
    `stay` int(11) unsigned default 0,
    `life`  int(11) default 365,
    `lastupdate` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,

    `birthday` date NOT NULL default '1990-01-01',
    `address` varchar(128), 
    `usertitle` varchar(20) NOT NULL default 'user',
    `gender`  int(11) unsigned default 1,
    `realname` varchar(20),

    `contact` varchar(80),
    `want` varchar(50),
    `job` varchar(80),
    `shai` varchar(140),
    `marriage` varchar(10),

    `about` text ,
    
    `dattr` blob,

    PRIMARY KEY (`uid`),
    UNIQUE KEY `userid` (`userid`)
) ENGINE=InnoDB  DEFAULT CHARSET=UTF8;


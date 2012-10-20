DROP TABLE IF EXISTS `argo_attachead`;
CREATE TABLE IF NOT EXISTS `argo_attachead` (
    `aid` int(11) unsigned NOT NULL auto_increment,

    `uploader` int(11) unsigned NOT NULL,
    `filename` varchar(20) unsigned NOT NULL,
    `filesize` int(11) unsigned NOT NULL,
    `filetype` varchar(10),
    `uploadtime` timestamp NOT NULL default CURRENT_TIMESTAMP,

    PRIMARY KEY (`aid`),
    KEY (`uid`)
    
) ENGINE=MyISAM  DEFAULT CHARSET=UTF8;

DROP TABLE IF EXISTS `argo_boardhead`;
CREATE TABLE IF NOT EXISTS `argo_boardhead` (
    `bid` int(11) unsigned NOT NULL auto_increment,
    `sid` int(11) unsigned NOT NULL,
    `boardname` varchar(20) NOT NULL,
    `description` varchar(50) NOT NULL,
    `bm` varchar(80),
    `flag` int(11) unsigned DEFAULT 0,
    `lastpost` int(11) NOT NULL default 0,
    
    -- `tp` varchar(20),
    -- `level` int(11) unsigned default 0, */
    -- `r_prem` int(11) unsigned DEFAULT 1, /* read permissions */
    -- `p_prem` int(11) unsigned DEFAULT 2, /* post permissions */
    -- `s_perm` int(11) unsigned DEFAULT 2, /* visible permissions */
    about varchar(80) ,
    welcome text ,

    PRIMARY KEY (`bid`),
    UNIQUE KEY `boardname` (`boardname`)
) ENGINE=MyISAM  DEFAULT CHARSET=UTF8;

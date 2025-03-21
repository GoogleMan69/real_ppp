-- SQLite
CREATE TABLE sys_user(
    userid INTEGER PRIMARY KEY,
    usermail VARCHAR(255) NOT NULL,
    userpwd VARCHAR(255) NOT NULL,
    errcnt INTEGER DEFAULT 0,
    lasttm CHAR(14) DEFAULT '',
    datest CHAR(08) DEFAULT '19110101',
    dateed CHAR(08) DEFAULT '29991231',
    lockuser CHAR(1) DEFAULT 'N'
);
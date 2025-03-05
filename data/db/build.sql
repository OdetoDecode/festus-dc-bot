create table if not exists exp(
    UserID integer primary key,
    XP integer default 0,
    level integer default 0,
    XPLock text default current_timestamp
);
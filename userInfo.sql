drop table if exists users;
create table users (
  id integer primary key autoincrement,
  name string not null,
  psw string not null,
  email string not null
);
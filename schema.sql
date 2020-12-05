
drop table if exists projects;
create table projects (
  id integer primary key autoincrement,
  'player_id' int not null
);
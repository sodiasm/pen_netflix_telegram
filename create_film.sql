CREATE TABLE films
(
film_name varchar(255) not null,
userId varchar(255) not null,
review varchar(2000) not null
);

insert into [dbo].[films] (film_name,userid,review) values ('Zombieland','Wailord','Zombieland is a good movie. It has many funny scenes. It also teaches us how to survive in zombie world. For example,  "Don''t be a hero", "Double tap" and "Cardio".')
# 使用管道迁移mysql数据

## mysql实例

- 源库：root/*password*@*source_ip*:*dbname*
- 目标：root/*password*@*target_ip*:*dbname*

## 迁移2018-01-01之前的所有pay_action记录

### 创建目标库

```
$ mysql -u root -h target_ip -p'password'
mysql> create database dbname;
```

### 创建通讯管道

```
$ mkfifo m.pipe
```

### 执行导出导入

时间 `2018-01-01 00:00:00` 对应的时间戳是 `1514736000`

1. 目标库导入

```
$ mysql -u root -h target_ip -p'password' dbname < m.pipe
```

2. 源库导出

```
$ mysqldump -uroot -p'password' -h source_ip --default-character-set=utf8 dbname --where=" postTime<'1514736000' " > m.pipe
```

3. 删除源库中的数据

批量生成delete sql，然后执行之。

```
mysql> SELECT CONCAT('delete from ', table_name, " where postTime<'1530374400';" ) FROM information_schema.tables WHERE table_schema='public_sdk' AND table_name LIKE 'pay_action_%';
```

4. 导入增量数据

```
$ mysqldump -uroot -p'password' -h source_ip --default-character-set=utf8 dbname --where=" postTime>='1530374400' " -t > m.pipe
```

### 注意点

- 增量条件一定要改变，这样数据不会重复
- 务必使用`-t`选项，这样导出的只有表数据没有表结构，才不会出现 `DROP TABLE IF EXISTS` 的语句，否则之前的导入都白费了


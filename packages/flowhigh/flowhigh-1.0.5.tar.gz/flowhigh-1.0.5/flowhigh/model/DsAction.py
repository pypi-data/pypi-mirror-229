from enum import Enum


class DsAction(Enum):
    delete = 1
    insert = 2
    update = 3
    create_view = 4
    create_table = 5
    create_stage = 6
    copy = 7
    add_fk = 8
    alter_fk = 9
    rename_fk = 10
    add_pk = 11
    alter_pk = 12
    rename_pk = 13
    drop_constraint = 14
    rename_table = 15
    add_index = 16
    drop_index = 17
    alter_index = 18
    rename_index = 19
    add_column = 20
    drop_column = 21
    alter_column = 22
    rename_column = 23


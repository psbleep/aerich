from tortoise import Tortoise

from aerich.ddl.mysql import MysqlDDL
from aerich.ddl.sqlite import SqliteDDL
from aerich.migrate import Migrate


def test_migrate():
    apps = Tortoise.apps
    models = apps.get("models")
    diff_models = apps.get("diff_models")
    Migrate.diff_models(diff_models, models)
    Migrate.diff_models(models, diff_models, False)
    if isinstance(Migrate.ddl, MysqlDDL):
        assert Migrate.upgrade_operators == [
            "ALTER TABLE `category` ADD `name` VARCHAR(200) NOT NULL",
            "ALTER TABLE `user` ADD UNIQUE INDEX `uid_user_usernam_9987ab` (`username`)",
        ]
        assert Migrate.downgrade_operators == [
            "ALTER TABLE `category` DROP COLUMN `name`",
            "ALTER TABLE `user` DROP INDEX `uid_user_usernam_9987ab`",
        ]
    elif isinstance(Migrate.ddl, SqliteDDL):
        assert Migrate.upgrade_operators == [
            'ALTER TABLE "category" ADD "name" VARCHAR(200) NOT NULL',
            'ALTER TABLE "user" ADD UNIQUE INDEX "uid_user_usernam_9987ab" ("username")',
        ]
        assert Migrate.downgrade_operators == [
            """PRAGMA foreign_keys=off;
        ALTER TABLE "category" RENAME TO "_category_old";
        CREATE TABLE IF NOT EXISTS "category" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "slug" VARCHAR(200) NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE /* User */
);
        INSERT INTO category (created_at, id, slug, user_id) SELECT created_at, id, slug, user_id FROM _category_old;
        DROP TABLE _category_old;
        PRAGMA foreign_keys=on;""",
            'ALTER TABLE "user" DROP INDEX "uid_user_usernam_9987ab"',
        ]

    else:
        assert Migrate.upgrade_operators == [
            'ALTER TABLE "category" ADD "name" VARCHAR(200) NOT NULL',
            'ALTER TABLE "user" ADD UNIQUE INDEX "uid_user_usernam_9987ab" ("username")',
        ]
        assert Migrate.downgrade_operators == [
            'ALTER TABLE "category" DROP COLUMN "name"',
            'ALTER TABLE "user" DROP INDEX "uid_user_usernam_9987ab"',
        ]

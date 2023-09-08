from .repository import Repository
import sqlite3

query_for_model = {
    "save": "INSERT INTO <modelname> (<attribute>, <attribute>, <attribute>) VALUES (<value>, <value>, <value>)",  # noqa E501
    "update": "UPDATE <modelname> SET <attribute> = <value>, <attribute> = <value>, <attribute> = <value> WHERE id = <id>",  # noqa E501
    # Select columns instead of * because we don't know the order in which they will be returned  # noqa E501
    "fetch_all": "SELECT <attribute>, <attribute>, <attribute>, <attribute> FROM <modelname>",  # noqa E501
    "delete_by_id": "DELETE FROM <modelname> WHERE id = <id>",
}


class SqlRepository(Repository):
    def execute_query(self, query):
        # Idea: Make guestbook the app's name somehow so it can be accessed globally?
        self.connection = sqlite3.connect("guestbook.db")
        cursor = self.connection.execute(query)
        self.connection.commit()

        # This will return an empty list if e.g. an INSERT is executed
        return cursor.fetchall()

    def get_object_variable_values_from_object(self, obj):
        return [
            (attr, getattr(obj, attr))
            for attr in dir(obj)
            if not callable(getattr(obj, attr))
            and not attr.startswith("__")
            and not attr == "id"
        ]

    def prepare_query(self, obj, instance_variables, query):
        query = query.replace("<modelname>", self._class_name)
        query = query.replace("<id>", str(obj.id))

        for attr, value in instance_variables:
            if "<attribute>" in query:
                query = query.replace("<attribute>", attr, 1)

            if "<value>" in query:
                if isinstance(value, str):
                    value = "'" + value + "'"
                query = query.replace("<value>", value, 1)

        return query

    def save(self, obj):
        if self.search_by_id(obj.id):
            # Update
            obj_variable_values = self.get_object_variable_values_from_object(obj)
            return self.execute_query(
                self.prepare_query(obj, obj_variable_values, query_for_model["update"])
            )
        else:
            # Add
            obj_variable_values = self.get_object_variable_values_from_object(obj)
            return self.execute_query(
                self.prepare_query(obj, obj_variable_values, query_for_model["save"])
            )

    def fetch_all(self):
        instance_variables = self.get_object_variable_values_from_object(self._class())
        instance_variables.append(("id", None))

        items = []
        for row in self.execute_query(
            self.prepare_query(
                self._class(), instance_variables, query_for_model["fetch_all"]
            )
        ):
            item = self._class()
            for i in range(len(instance_variables)):
                setattr(item, instance_variables[i][0], row[i])
            items.append(item)

        return items

    def search_by_id(self, id):
        obj_to_find = None
        for obj in self.fetch_all():
            if obj.id == id:
                obj_to_find = obj
                break

        return obj_to_find

    def search_by_attributes(self, attributes):
        items = []
        for obj in self.fetch_all():
            found = True
            for property, value in attributes.items():
                if not getattr(obj, property) == value:
                    found = False

            if found:
                items.append(obj)

        return items

    def delete(self, id):
        if not self.search_by_id(id):
            return False
        else:
            return self.execute_query(
                self.prepare_query(self._class(id), {}, query_for_model["delete_by_id"])
            )

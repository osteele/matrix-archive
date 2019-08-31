from mongoengine import DateTimeField, Document, DynamicField, StringField


class Message(Document):
    room_id = StringField(r'!.+:.+', required=True)
    event_id = StringField(r'\$.+', required=True, unique_with='room_id')
    sender = StringField(r'@.+:.+', required=True)
    user_id = StringField(r'@.+:.+', required=False)
    messageType = StringField(r'm\.room\.message', db_field='type', required=True)
    timestamp = DateTimeField(required=True)
    content = DynamicField(required=True)

    def is_image(self):
        return self.content.get('msgtype') == 'm.image'

    @property
    def image_url(self):
        return self.content['url'] if self.is_image() else None

    @property
    def thumbnail_url(self):
        return (self.content['info'].get('thumbnail_url')
                if self.is_image() else None)

# coding: utf8

from sanic import Sanic
from sanic.response import html

from mmongo.document import Document
from mmongo.fields import NumericField, StringField

app = Sanic(__name__)

MONGO = 'mongodb://127.0.0.1:27017/mmongo'  # noqa
app.config['MONGO'] = MONGO

Document.set_application(app)


class Hotel(Document):
    f_test_one = StringField(required=True)
    f_test_two = NumericField(required=True, default=2)


@app.get('/')
async def index(request):
    model = Hotel()
    # await model.save()
    result = []
    cursor = await model.find()
    async for m in cursor:
        del m['f_test_one']
        await m.save()
        result.append(m._id)
    return html(result)


if __name__ == '__main__':
    app.run()

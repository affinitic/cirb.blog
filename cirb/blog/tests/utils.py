

class FakeContext(object):

    def __init__(self):
        self.id = "myid"
        self.title = "a title"
        self.description = "a description"
        self.creators = ["myself"]
        self.date = "a date"
        self.aq_inner = self
        self.aq_parent = None
        self._modified = "modified date"
        self.language = "fr"
        self.portal_type = "Topic"
        self.text = "text"
        self.image_caption = "image caption"

    def getId(self):
        return self.id

    def Title(self):
        return self.title

    def Creators(self):
        return self.creators

    def Description(self):
        return self.description

    def Date(self):
        return self.date

    def modified(self):
        return self._modified

    def getPhysicalPath(self):
        return ('/', 'a', 'not', 'existing', 'path')

    def getFolderContents(self, filter=None):
        catalog = FakeCatalog()
        return catalog.searchResults()

    def absolute_url(self):
        return "http://nohost.com/" + self.id

    def queryCatalog(self, **kwargs):  # fake Topic
        catalog = FakeCatalog()
        return catalog.searchResults()

    def getEffectiveDate(self):
        return 'date 1'

    def getField(self, fieldname):
        return None

    def Language(self):
        return self.language

    def getText(self):
        return self.text

    def getImageCaption(self):
        return self.image_caption


class FakeBrain(object):
    def __init__(self):
        self.Title = ""
        self.Description = ""
        self.getId = ""
        self.portal_type = ""
        self.Creator = ""
        self.UID = "azerty"
        self.Subject = "keyword1"
        self.EffectiveDate = "yesterday"

    def getURL(self):
        return "http://fakebrain.com"

    def getObject(self):
        ob = FakeContext()
        ob.title = self.Title

        return ob


class FakeCatalog(object):
    def __call__(self, **kwargs):
        return self.searchResults(**kwargs)

    def searchResults(self, **kwargs):
        brain1 = FakeBrain()
        brain1.Title = "My first article"
        brain1.Creator = "myself"
        brain2 = FakeBrain()
        brain2.Title = "A great event"
        brain2.Description = "you will drink lots of beer"
        brain2.Creator = "myself"
        return [brain1, brain2]

    def modified(self):
        return '654654654654'


class FakePortalState(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def language(self):
        return self.context.Language()


class FakeUser(object):
    def __init__(self):
        self.id = ""
        self.fullname = ""
        self.email = ""

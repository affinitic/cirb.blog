from plone.app.testing import *
import cirb.blog


FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=cirb.blog,
                                additional_z2_products=[],
                                gs_profile_id='cirb.blog:default',
                                name="cirb.blog:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="cirb.blog:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="cirb.blog:Functional")

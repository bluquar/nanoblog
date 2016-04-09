export EMAIL_HOST=smtp.andrew.cmu.edu
export EMAIL_PORT=465
export EMAIL_USER=cmbarker
export EMAIL_PASSWORD='Cyanide250a!'
export NB_SECRET_KEY='9hi%uk&)00f34wv-4)m5nbrf6m@d0f3_u1&$xit@faad&nfsem'

export NB_S3_ACCESS_KEY='AKIAJRSROWWNK7ZAT7RA'
export NB_S3_SECRET_KEY='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'
export NB_S3_BUCKET='nanoblog'

heroku config:set EMAIL_HOST=smtp.andrew.cmu.edu EMAIL_PORT=465 EMAIL_USER=cmbarker EMAIL_PASSWORD='Cyanide250a!' NB_SECRET_KEY='9hi%uk&)00f34wv-4)m5nbrf6m@d0f3_u1&$xit@faad&nfsem'

heroku config:set NB_S3_ACCESS_KEY='AKIAJRSROWWNK7ZAT7RA'
heroku config:set NB_S3_SECRET_KEY='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'
heroku config:set NB_S3_BUCKET='nanoblog'

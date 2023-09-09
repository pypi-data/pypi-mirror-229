#  Copyright (c) 2023. SYSNET s.r.o.
#  All rights reserved.
#
class PdfError(Exception):
    def __init__(self, status=500, message="PDF exception", module=None):
        self.status = status
        self.message = message
        self.module = module
        super().__init__(self.message)

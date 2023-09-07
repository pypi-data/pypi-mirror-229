from jdw.mfc.entropy.deformer.fusionx.base import Base


class Futures(Base):

    def __init__(self,
                 batch,
                 freq,
                 horizon,
                 id=None,
                 directory=None,
                 is_full=False):
        super(Futures, self).__init__(batch=batch,
                                      freq=freq,
                                      horizon=horizon,
                                      id=id,
                                      directory=directory,
                                      is_full=is_full)

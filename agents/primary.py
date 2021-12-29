


    @staticmethod
    def add(fullPath : str):
        logging.info(f"adding: {fullPath}")

        Session = sessionmaker(engine)
        with Session() as session:
            p = Path.findRoot(fullPath)
            rel_path = fullPath.replace(p.windows, "")
            im = Image(rel_path, os.stat(fullPath).st_size, p)
            session.add(im)
            session.commit()


@staticmethod
    def findRoot(filePath : str):
        candidates = []
        Session = sessionmaker(engine)
        with Session() as session:
            for p in session.query(Path).all():
                if filePath.startswith(p.windows):
                    candidates.append((len(p.windows), p))
        if len(candidates)<=0:
            raise Exception(f"unable to find root path for: {filePath}")
            # TODO: create?
        return sorted(candidates)[-1][1]
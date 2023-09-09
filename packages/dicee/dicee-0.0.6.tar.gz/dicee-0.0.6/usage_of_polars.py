
@timeit
def load_with_polars(deserialize_flag):
    print(f'Deserialization Path: {deserialize_flag}\n')
    entity_to_idx = polars.read_parquet(deserialize_flag + '/entity_to_idx')
    polars.read_parquet(deserialize_flag + '/relation_to_idx')

    print(entity_to_idx)
    exit(1)
    self.kg.entity_to_idx = dict(
        zip(self.kg.entity_to_idx['entity'].to_list(), list(range(len(self.kg.entity_to_idx)))))
    self.kg.relation_to_idx = dict(
        zip(self.kg.relation_to_idx['relation'].to_list(), list(range(len(self.kg.relation_to_idx)))))

    self.kg.train_set = polars.read_parquet(self.kg.deserialize_flag + '/idx_train_df').to_numpy()
    self.kg.train_set = numpy_data_type_changer(self.kg.train_set,
                                                num=max(self.kg.num_entities, self.kg.num_relations))

    try:
        print('[5 / 4] Deserializing integer mapped data and mapping it to numpy ndarray...')
        self.kg.valid_set = polars.read_parquet(self.kg.deserialize_flag + '/idx_valid_df').to_numpy()
        self.kg.valid_set = numpy_data_type_changer(self.kg.valid_set,
                                                    num=max(self.kg.num_entities, self.kg.num_relations))

        print('Done!\n')
    except FileNotFoundError:
        print('No valid data found!\n')
        self.kg.valid_set = None

    try:
        print('[6 / 4] Deserializing integer mapped data and mapping it to numpy ndarray...')
        self.kg.test_set = polars.read_parquet(self.kg.deserialize_flag + '/idx_test_df').to_numpy()
        self.kg.test_set = numpy_data_type_changer(self.kg.test_set,
                                                   num=max(self.kg.num_entities, self.kg.num_relations))
        print('Done!\n')
    except FileNotFoundError:
        print('No test data found\n')
        self.kg.test_set = None

    if self.kg.eval_model:
        if self.kg.valid_set is not None and self.kg.test_set is not None:
            # 16. Create a bijection mapping from subject-relation pairs to tail entities.
            data = np.concatenate([self.kg.train_set, self.kg.valid_set, self.kg.test_set])
        else:
            data = self.kg.train_set
        print('[7 / 4] Creating er,re, and ee type vocabulary for evaluation...')
        start_time = time.time()
        self.kg.er_vocab = get_er_vocab(data)
        self.kg.re_vocab = get_re_vocab(data)
        # 17. Create a bijection mapping from subject-object pairs to relations.
        self.kg.ee_vocab = get_ee_vocab(data)
        self.kg.domain_constraints_per_rel, self.kg.range_constraints_per_rel = create_constraints(
            self.kg.train_set)
        print(f'Done !\t{time.time() - start_time:.3f} seconds\n')

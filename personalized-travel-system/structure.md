# ��Ŀ�ṹ

```plaintext
personalized_travel_system/
������ backend/                   # ��ˣ�Flask API��
��   ������ app.py                 # Flask ��Ӧ�����
��   ������ config.py              # �����ļ������ݿ⡢��Կ�ȣ�
��   ������ requirements.txt       # Python �����嵥
��   ������ schema.sql             # MySQL ���ݿ��ṹ
��   ������ static/                # ��̬��Դ�����ϴ�ͼƬ��
��   ������ routes/                # ��� API �߼���Flask Blueprint��
��   ��   ������ __init__.py        # Blueprint ��ʼ��
��   ��   ������ auth.py            # �û���¼��ע��
��   ��   ������ recommend.py       # ����/��ʳ/�μ��Ƽ�
��   ��   ������ search.py          # ��������
��   ��   ������ map.py             # ��ͼ��� API��·���滮����ʩ��ѯ��
��   ��   ������ diary.py           # �����ռ� API
��   ��   ������ food.py            # ��ʳ API
��   ��   ������ indoor.py          # ���ڵ��� API
��   ��   ������ aigc.py            # AI �������� API��Stable Diffusion��
��   ������ models/                # ���ݿ�ģ�ͣ�SQLAlchemy ORM��
��   ��   ������ __init__.py        # �������ݿ�
��   ��   ������ user.py            # �û�ģ��
��   ��   ������ place.py           # ����ģ��
��   ��   ������ food.py            # ��ʳģ��
��   ��   ������ diary.py           # �����ռ�ģ��
��   ��   ������ path.py            # ·���滮���ݽṹ
��   ������ utils/                 # ���ߺ���
��   ��   ������ helpers.py         # �������ߺ�����������롢��ʽת���ȣ�
��   ��   ������ security.py        # ���� & ��Ȩ
��   ������ tests/                 # ��Ԫ����
��   ������ wsgi.py                # �������� WSGI ��ڣ�Gunicorn��
��
������ frontend/                  # ǰ�ˣ�Vue.js / React��
��   ������ public/                # ��̬��Դ
��   ������ src/                   # ��Ҫǰ�˴���
��   ��   ������ assets/            # ͼƬ��CSS
��   ��   ������ components/        # Vue ���
��   ��   ������ views/             # ҳ���������ҳ���������Ƽ�����ͼ�ȣ�
��   ��   ������ router.js          # Vue Router ·������
��   ��   ������ store.js           # Vuex/Pinia ״̬����
��   ��   ������ main.js            # Vue ���
��   ������ package.json           # ǰ�������嵥
��   ������ vite.config.js         # Vite ���ã���������
��
������ database/                  # ���ݹ������ݳ�ʼ�� & �ű���
��   ������ init_db.py             # ��ʼ�����ݿ⣨���� & ����ʾ�����ݣ�
��   ������ migrate.py             # ���ݿ�Ǩ�ƣ�������ֶΣ�
��   ������ seed_data.sql          # Ԥ�����ݣ��û������㡢��ʳ�ȣ�
��
������ crawler/                   # ���棨��ȡ��ʵ��ͼ & ��ʳ���ݣ�
��   ������ scrape_osm.py          # ͨ�� OpenStreetMap ��ȡ��· & ��ʩ����
��   ������ scrape_food.py         # ��ȡ��ʳ���ݣ��ߵ� API / �ٶ� API��
��   ������ scrape_places.py       # ��ȡ���� & У԰��Ϣ
��   ������ data/                  # �洢��ȡ�� JSON / CSV ����
��
������ ai_recommendation/         # AI �Ƽ������Ի��Ƽ� & AIGC��
��   ������ content_based.py       # ���������Ƽ���Word2Vec / BERT��
��   ������ collaborative_filter.py# Эͬ�����Ƽ����û���Ϊ������
��   ������ vector_search.py       # �������ݿ� ANN �������������
��   ������ generate_animation.py  # �������ζ�����Stable Diffusion��
��
������ docs/                      # �ĵ�
��   ������ API_Documentation.md   # API ˵���ĵ���Swagger/Postman �ο���
��   ������ README.md              # ��Ŀ���� & ����ָ��
��   ������ setup_guide.md         # ��װ & ����ָ��
��   ������ development_guide.md   # ���� & ����ָ��
��
������ scripts/                   # ���� & ά���ű�
��   ������ start_dev.sh           # ��������������ǰ��� & ���ݿ⣩
��   ������ deploy.sh              # ���𵽷������Ľű�
��   ������ backup_db.sh           # �������ݿ�
��
������ .gitignore                 # Git �����ļ����ų� venv��node_modules �ȣ�
������ docker-compose.yml         # Docker Compose ���ã�����Ҫ��������
������ LICENSE                    # ���֤����ѡ��
```


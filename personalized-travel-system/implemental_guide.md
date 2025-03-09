# **? ���Ի������Ƽ�ϵͳ - ����ָ��**

## **? ��Ŀ����˳�� & ����ֽ�**

��ָ����ϸ������ΰ��� **��� �� ���ݿ� �� ���� �� AI �� ǰ�� �� ����** ��˳�򿪷� **���Ի������Ƽ�ϵͳ**��

---

## **? 1. ���ú�˿�ܣ�Flask��**
**? `backend/`**

> **Ŀ��**��� Flask ��Ӧ�ã��������ݿ⣬ע�� API ��ͼ��

? **����**
1. **���� `app.py`**��Flask ����ڣ�
   - ��ʼ�� Flask
   - ���� MySQL ���ݿ�
   - ע�� API ��ͼ
   - ����������

2. **���� `config.py`**���������ݿ⡢JWT ��Կ��
   - MySQL ���Ӳ���
   - JWT ��֤��Կ

3. **��д `requirements.txt`**����װ����������
   - `Flask`��`SQLAlchemy`��`Flask-JWT-Extended`��`Flask-CORS`

4. **��ʼ�� `schema.sql`**������ MySQL ��ṹ��

5. **��д `wsgi.py`**���������� WSGI ��ڣ�

6. **���� `routes/` Ŀ¼����д API ģ��**
   - `routes/auth.py`���û���֤ API��
   - `routes/recommend.py`���Ƽ�ϵͳ API��
   - `routes/search.py`���������� API��
   - `routes/map.py`��·���滮 API��
   - `routes/diary.py`�������ռ� API��
   - `routes/food.py`����ʳ API��
   - `routes/indoor.py`�����ڵ��� API��
   - `routes/aigc.py`��AI �������� API��

---

## **? 2. ������ݿ⣨MySQL + SQLAlchemy��**
**? `backend/models/`**

> **Ŀ��**��������ݿ��ṹ��֧�����к��Ĺ��ܡ�

? **����**
1. **���� `models/__init__.py`**�����ݿ��ʼ����
2. **���� `models/user.py`**���û�ģ�ͣ�
3. **���� `models/place.py`**������ģ�ͣ�
4. **���� `models/food.py`**����ʳģ�ͣ�
5. **���� `models/diary.py`**�������ռ�ģ�ͣ�
6. **���� `models/path.py`**��·���滮���ݽṹ��
7. **���� `database/init_db.py`**���������ݿ�� & ����������ݣ�

---

## **? 3. ��ȡ��ͼ & ��ʳ����**
**? `crawler/`**

> **Ŀ��**����ȡ **��ʵ��У԰ & �����ͼ����**���Լ� **��ʳ����**��

? **����**
1. **��д `crawler/scrape_osm.py`**����ȡ OpenStreetMap ��ͼ���ݣ�
2. **��д `crawler/scrape_places.py`**����ȡ���� & ѧУ���ݣ�
3. **��д `crawler/scrape_food.py`**����ȡ��ʳ���ݣ�
4. **�洢���ݵ� `crawler/data/`**
5. **�������ݲ����� MySQL**

---

## **? 4. ʵ�� AI �Ƽ�ϵͳ**
**? `ai_recommendation/`**

> **Ŀ��**��ʹ�� AI ʵ�ָ��Ի��Ƽ� & ���ζ������ɡ�

? **����**
1. **��д `content_based.py`**���������ݵ��Ƽ���
2. **��д `collaborative_filter.py`**��Эͬ�����Ƽ���
3. **��д `vector_search.py`**���������ݿ� + ���������������
4. **��д `generate_animation.py`**��Stable Diffusion �������ζ�����

---

## **? 5. �ǰ�ˣ�Vue.js / React��**
**? `frontend/`**

> **Ŀ��**������ǰ�˽��棬���Ӻ�� API��ʵ�ֵ�ͼ���ӻ���

? **����**
1. **���� `package.json`**������ Vue.js / React ������
2. **���� `vite.config.js`**���������
3. **���� `src/main.js`**��ǰ����ڣ�
4. **���� `src/router.js`**��Vue Router ���ã�
5. **���� `src/store.js`**��Vuex / Pinia ״̬����
6. **���� `views/` ҳ�����**
7. **���� `components/` �����**

---

## **? 6. ��д���� & �ĵ�**
**? `docs/`**

> **Ŀ��**��׫д API �ĵ�����װָ�� & �������ֲᡣ

? **����**
1. **���� `README.md`**����Ŀ���ܣ�
2. **���� `API_Documentation.md`**��API ˵���ĵ���
3. **���� `setup_guide.md`**����װ & ����ָ�ϣ�
4. **���� `development_guide.md`**������ & ����ָ�ϣ�

---

## **? 7. ���� & ����**
**? `scripts/`**

> **Ŀ��**��������Ŀ�����𵽷�������

? **����**
1. **���� `scripts/start_dev.sh`**������ Flask & Vue.js ����������
2. **���� `scripts/deploy.sh`**���Զ�����ű���
3. **���� `scripts/backup_db.sh`**�����ݿⱸ�ݽű���

---

## **? 8. ������Ŀ**

```bash
# ��װ�������
cd backend
pip install -r requirements.txt

# ��ʼ�����ݿ�
python database/init_db.py

# ���� Flask ������
python backend/app.py

# ��װǰ������
cd frontend
npm install

# ����ǰ��
npm run dev

# ��������
python crawler/scrape_osm.py

# ���� AI �Ƽ�
python ai_recommendation/content_based.py
```

---

## **? �ܽ�**
? **���**��Flask API��
? **���ݿ�**��MySQL��
? **��ȡ��ʵ����**��OpenStreetMap / �ߵ� API��
? **AI �Ƽ�ϵͳ**��Word2Vec / BERT / Stable Diffusion��
? **ǰ�˿���**��Vue.js / React��
? **�������**

? **���ˣ���ĸ��Ի������Ƽ�ϵͳ��׼��������** ?

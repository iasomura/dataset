import psycopg2
from psycopg2 import sql
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

# データベースに接続する関数
def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"データベース接続エラー: {e}")
        return None

# website_dataテーブルのstatusカラムを97で更新する関数
def update_status_to_97(connection, website_id):
    try:
        with connection.cursor() as cursor:
            update_query = sql.SQL("""
                UPDATE website_data
                SET status = 97
                WHERE id = %s
            """)
            cursor.execute(update_query, (website_id,))
            connection.commit()
            print(f"ID {website_id} のステータスを97に更新しました。")
    except Exception as e:
        print(f"ステータス更新エラー: {e}")

# website_dataテーブルから特定のwebsite_idに基づいてレコードを確認する関数
def check_write_status(website_id):
    connection = connect_to_db()
    
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # website_dataテーブルの指定IDのレコードを取得
            query = sql.SQL("""
            SELECT https_certificate_all, https_certificate_issuer, screenshot_availability, 
                   mhtml_pc_site, status 
            FROM website_data 
            WHERE id = %s
            """)
            cursor.execute(query, (website_id,))
            result = cursor.fetchone()
            
            if result:
                columns = ['https_certificate_all', 'https_certificate_issuer', 'screenshot_availability', 'mhtml_pc_site', 'status']
                record = dict(zip(columns, result))

                # 各カラムが正しく書き込まれているか確認
                if any(value is None for key, value in record.items() if key != 'status'):
                    print(f"書き込みが不完全: {record}")
                    update_status_to_97(connection, website_id)  # ステータスを97に更新
                    return False
                return True
            else:
                print(f"website_dataにID {website_id}のレコードが存在しません。")
                return False
    except Exception as e:
        print(f"クエリ実行エラー: {e}")
        return False
    finally:
        connection.close()

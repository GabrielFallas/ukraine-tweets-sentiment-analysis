from sqlalchemy import create_engine, text

engine = create_engine('postgresql://airflow:airflow@localhost:5432/airflow')

with engine.connect() as conn:
    # Get sentiment distribution
    result = conn.execute(text('''
        SELECT sentiment, COUNT(*) as count 
        FROM ukraine_tweets_sentiment 
        GROUP BY sentiment 
        ORDER BY sentiment
    '''))

    print('\nSentiment Distribution:')
    for row in result:
        print(f'  {row[0]}: {row[1]} tweets')

    # Get total
    result2 = conn.execute(
        text('SELECT COUNT(*) FROM ukraine_tweets_sentiment'))
    print(f'\nTotal: {result2.scalar()} tweets')

    print('\n✓ Data successfully loaded to PostgreSQL!')

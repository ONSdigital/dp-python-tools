import setup_s3
import  os

if __name__ == '__main__':
    
    bucket1 = setup_s3.setup()
    # bucket1.create_bucket('mo-rich-test-bucket' , 'eu-west-2')
    # print('Bucket created successfully')
    bucket1.upload_file('s3/test.json', 'mo-rich-test-bucket')
    print('Bucket uploaded successfully') 

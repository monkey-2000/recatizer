# for path in cat.paths:
#     cat_image = self.s3_client.load_image(path)
#     cat_image = cv2.cvtColor(cat_image, cv2.COLOR_BGR2RGB)
#     cat_image_bytes = cv2.imencode(".jpg", cat_image)[1].tobytes()
#     media_group.append(InputMediaPhoto(media=cat_image_bytes))
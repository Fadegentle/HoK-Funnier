import 'package:flutter/material.dart';

class MyImageWidget extends StatefulWidget {
  const MyImageWidget({super.key});

  @override
  State<MyImageWidget> createState() => MyImageWidgetState();
}

class MyImageWidgetState extends State<MyImageWidget> {
  String imageUrl = 'http://192.168.50.46:8000/random/hero/image';

  void reloadImage() {
    setState(() {
      imageUrl += '?timestamp=${DateTime.now().millisecondsSinceEpoch}';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Image.network(
          imageUrl,
          loadingBuilder: (context, child, progress) {
            if (progress == null) {
              return child;
            }
            return const CircularProgressIndicator();
          },
          errorBuilder: (context, error, stackTrace) {
            return const Text('图片加载失败');
          },
        ),
        ElevatedButton(
          onPressed: reloadImage,
          child: const Text('随机抽取'),
        ),
      ],
    );
  }
}

void main() {
  runApp(MaterialApp(
    home: Scaffold(
      appBar: AppBar(
        title: const Text('随机英雄'),
      ),
      body: Center(
        child: MyImageWidget(),
      ),
    ),
  ));
}

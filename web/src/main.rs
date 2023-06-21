use actix_web::{get, App, HttpResponse, HttpServer};
use std::fs;
use std::path::{PathBuf};
use rand::seq::SliceRandom;
use std::io::Read;


fn get_jpg_files(folder_path: &str) -> Vec<PathBuf> {
    let mut image_paths = Vec::new();

    if let Ok(entries) = fs::read_dir(folder_path) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_file() && path.extension().map(|ext| ext == "jpg").unwrap_or(false) {
                    image_paths.push(path);
                } else if path.is_dir() {
                    image_paths.extend(get_jpg_files(&path.to_string_lossy()));
                }
            }
        }
    }

    image_paths
}

#[get("/")]
async fn random_image() -> HttpResponse {
    // 从某个文件夹中获取所有图片文件路径
    let image_folder = "../heroes";
    let image_paths = get_jpg_files(image_folder);

    // 随机选择一个图片路径
    let random_image_path = image_paths
        .choose(&mut rand::thread_rng())
        .unwrap_or(&PathBuf::from("default_image.jpg")).to_owned();

    // 读取图片数据
    let mut img = fs::File::open(random_image_path).expect("Failed to open image file");
    let mut buffer = Vec::new();
    if img.read_to_end(&mut buffer).is_err() {
        return HttpResponse::InternalServerError().body("Failed to read image file");
    }

    println!("{:?}", img);
    // 返回随机图片的数据
    HttpResponse::Ok().content_type("image/jpeg").body(buffer)
}


#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(random_image)
    })
        .bind("127.0.0.1:8000")?
        .run()
        .await
}

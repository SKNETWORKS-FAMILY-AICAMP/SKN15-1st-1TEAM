CREATE TABLE car_model (
    idx INT AUTO_INCREMENT PRIMARY KEY COMMENT '인덱스',
    years INT DEFAULT NULL COMMENT '연도',
    months INT DEFAULT NULL COMMENT '월',
    carType VARCHAR(10) NOT NULL COMMENT '모델코드',
    brand_code int NOT NULL COMMENT '브랜드',
    model_name VARCHAR(10) NOT NULL COMMENT '모델'
    model_code int NOT NULL COMMENT '모델코드',
    image_link VARCHAR(1000) DEFAULT NULL COMMENT '이미지 링크',
    volume BIGINT DEFAULT NULL COMMENT '판매량',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '등록일',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일'
    
) COMMENT='월별차량모델순위';

CREATE TABLE car_brand (
    idx INT AUTO_INCREMENT PRIMARY KEY COMMENT '인덱스',
    years INT NOT NULL COMMENT '연도',
    months INT NOT NULL COMMENT '월',
    brand_name VARCHAR(30) NOT NULL COMMENT '브랜드',
    volume BIGINT DEFAULT NULL COMMENT '판매량',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '등록일',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일'
) COMMENT='월별차량브랜드순위';

CREATE TABLE origin (
    code VARCHAR(5) PRIMARY KEY COMMENT '원산지 코드',
    name VARCHAR(10) NOT NULL COMMENT '원산지명'
) COMMENT='원산지 코드 테이블';

CREATE TABLE ownership_type (
    code VARCHAR(5) PRIMARY KEY COMMENT '소유구분 코드',
    name VARCHAR(30) NOT NULL COMMENT '소유구분명'
) COMMENT='소유구분 코드 테이블';

CREATE TABLE car_type (
    code VARCHAR(5) PRIMARY KEY COMMENT '차종 코드',
    name VARCHAR(20) NOT NULL COMMENT '차종명'
) COMMENT='차종 코드 테이블';

CREATE TABLE age_group (
    code VARCHAR(5) PRIMARY KEY COMMENT '연령대 코드',
    name VARCHAR(20) NOT NULL COMMENT '연령대명'
) COMMENT='연령대 코드 테이블';

CREATE TABLE acquisition_price (
    code VARCHAR(5) PRIMARY KEY COMMENT '취득가 코드',
    name VARCHAR(100) NOT NULL COMMENT '취득가명'
) COMMENT='취득가 코드 테이블';

CREATE TABLE fuel_type (
    code VARCHAR(5) PRIMARY KEY COMMENT '연료 코드',
    name VARCHAR(30) NOT NULL COMMENT '연료명'
) COMMENT='연료 코드 테이블';

CREATE TABLE engine_displacement (
    code VARCHAR(5) PRIMARY KEY COMMENT '배기량 코드',
    name VARCHAR(100) NOT NULL COMMENT '배기량명'
) COMMENT='배기량 코드 테이블';

CREATE TABLE carUsage (
    code VARCHAR(5) PRIMARY KEY COMMENT '용도 코드',
    name VARCHAR(30) NOT NULL COMMENT '용도명'
) COMMENT='용도 코드 테이블';

CREATE TABLE car_365 (
    idx INT AUTO_INCREMENT PRIMARY KEY COMMENT '인덱스',
    brand VARCHAR(50) NOT NULL COMMENT '브랜드',
    model_name VARCHAR(100) NOT NULL COMMENT '모델명',
    purchase_count BIGINT NOT NULL COMMENT '구매대수',
    origin_code VARCHAR(5) NOT NULL COMMENT '국산/수입 코드',
    ownership_type_code VARCHAR(5) NOT NULL COMMENT '소유구분 코드',
    car_type_code VARCHAR(5) NOT NULL COMMENT '차종 코드',
    age_group_code VARCHAR(5) NOT NULL COMMENT '연령대 코드',
    acquisition_price_code VARCHAR(5) NOT NULL COMMENT '취득가 코드',
    fuel_type_code VARCHAR(5) NOT NULL COMMENT '연료 코드',
    engine_displacement_code VARCHAR(5) NOT NULL COMMENT '배기량 코드',
    FOREIGN KEY (origin_code) REFERENCES origin(code),
    FOREIGN KEY (ownership_type_code) REFERENCES ownership_type(code),
    FOREIGN KEY (car_type_code) REFERENCES car_type(code),
    FOREIGN KEY (age_group_code) REFERENCES age_group(code),
    FOREIGN KEY (acquisition_price_code) REFERENCES acquisition_price(code),
    FOREIGN KEY (fuel_type_code) REFERENCES fuel_type(code),
    FOREIGN KEY (engine_displacement_code) REFERENCES engine_displacement(code)
) COMMENT='자동차 365 메인 테이블';

create table car_region_type_data(
	years int not null comment "연도",
	months int not null comment "월",
	city_1 varchar(30) not null comment "도시1",
	city_2 varchar(30) not null comment "도시2",
	itm varchar(100) not null comment "구분",
	volume bigint not null comment "판매량") comment '지역별 차량 타입';
	
create table brand_logo(
	brand varchar (100) not NULL COMMENT "브랜드",
	codes int(30) not NULL COMMENT "코드",
	img_link varchar (1000) not NULL COMMENT  "이미지링크") COMMENT "브랜드로고";

create table FAQ(
	faq_nm int not null comment "FAQ 번호",
	mfr_id varchar (50) comment "제조사",
	categories varchar (50) comment "카테고리",
	question varchar (10000) comment "질문",
	answer varchar (10000) comment "답변",
	primary key (faq_nm),
	foreign key (mfr_id) reference car_brand(brand_name)) comment "FAQ"

CREATE TABLE car_brand_data (
    idx INT AUTO_INCREMENT PRIMARY KEY COMMENT '인덱스',
    years INT NOT NULL COMMENT '연도',
    months INT NOT NULL COMMENT '월',
    brand_code int NOT NULL COMMENT '브랜드코드',
    volume BIGINT DEFAULT NULL COMMENT '판매량',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '등록일',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일'
) COMMENT='월별차량브랜드순위';

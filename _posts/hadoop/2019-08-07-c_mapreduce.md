---
layout: post
title: mapreduce
category: hadoop
tags: [hadoop]
comments: false
---

# [mapreduce]()

## 학습
* MapReduce 이해하기
* WordCount2.java 수정 - 자료형 변경
* jar 파일 생성하여 nn01의 ~/source로 전송
* yarn으로 실행(입력: 10K.ID.CONTENTS)

## 실습
* WordCount2
    1. sample.WordCount2.java 생성
    ~~~java
    package sample;

    import java.io.IOException;
    import java.util.StringTokenizer;

    import org.apache.hadoop.conf.Configuration;
    import org.apache.hadoop.fs.Path;
    import org.apache.hadoop.io.IntWritable;
    import org.apache.hadoop.io.Text;
    import org.apache.hadoop.mapreduce.Job;
    import org.apache.hadoop.mapreduce.Mapper;
    import org.apache.hadoop.mapreduce.Reducer;
    import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
    import org.apache.hadoop.mapreduce.lib.input.KeyValueTextInputFormat;
    import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
    import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

    public class WordCount2 
    {	
        public static class MyMapper extends Mapper<Text, Text, Text, IntWritable> 
    /*
        입력<key, value> : <Text, Text>
        입력키 : 글 번호
        입력값 : 한줄 내용
        
        출력<key, value> : <Text, Int>
        출력키 : 한 단어
        출력값  : 1
    */
        {
            // 출력 Key, value
            private Text word = new Text();
            private final static IntWritable one = new IntWritable(1);

            public void map(Text Key, Text value, Context context) throws IOException, InterruptedException 
            {
                // 문자열로 자라준다.
                String line = value.toString();
                // 모든 이유로 잘라준다.
                StringTokenizer itr = new StringTokenizer(line, "\t\r\n\f |:;,.()<>'\"-!?");
                while(itr.hasMoreTokens()) 
                {
                    word.set(itr.nextToken());
                    context.write(word, one);
                } // while-end
            } // end of main
        } // end of MyMapper
        
        public static class MyReducer extends Reducer<Text, IntWritable, Text, IntWritable> 
        // 입력<key, value> : <Int, Text>
        // 출력<key, value> : <Text, Int>
        {
            
            private IntWritable result = new IntWritable();
            
            public void reduce(Text key, Iterable<IntWritable> value, Context context) throws IOException, InterruptedException {
                int sum = 0;
                for(IntWritable val : value) {
                    sum += val.get();
                } // end of for
                
                result.set(sum); // java int형 -> hadoop LongWritable형으로 지정
                context.write(key, result);
            } // end of reduce
        } // end of MyReducer
        
        public static void main(String[] args) throws Exception
        {
            Configuration conf = new Configuration();
            if(args.length != 2) {
                System.out.println("사용: WordCount2 <input> <output>");
                System.exit(2);
            } // end of if
            
            Job job = Job.getInstance(conf, "WordCount2");
            
            // 각 클래스 지정
            job.setJarByClass(WordCount2.class);
            job.setMapperClass(MyMapper.class);
            job.setReducerClass(MyReducer.class);
            
            // 출력 key와 value 타입 지정
            job.setOutputKeyClass(Text.class);
            job.setOutputValueClass(IntWritable.class);
            
            // 입력포맷과 출력포맷 지정(*****)
            job.setInputFormatClass(KeyValueTextInputFormat.class);
            job.setOutputFormatClass(TextOutputFormat.class);
            
            // 파일입력포맷과 파일출력포맷 지정
            FileInputFormat.addInputPath(job, new Path(args[0]));
            FileOutputFormat.setOutputPath(job, new Path(args[1]));
            
            // job을 실행
            // job이 다 실행하고 끝날때까지 기다리기
            job.waitForCompletion(true);
        } // end of main
    } // end of WordCount2
    ~~~
    2. WinCSP 업로드 후
    <br> 1) ls /home/hadoop/source
    <br> 2) yarn jar /home/hadoop/source/lab1.jar sample.WordCount2 /input/data/wiki/10K.ID.CONTENTS /output/wordcount2
    <br> 3) hdfs dfs -ls /output/wordcount2
    <br> 4) hdfs dfs -cat /output/wordcount2/part-r-00000

* TopNMain
    1. sample2class.TopNMain 생성
    ~~~java
    package sample2class;

    import java.io.IOException;
    import java.util.Comparator;
    import java.util.PriorityQueue;

    import org.apache.hadoop.conf.Configuration;
    import org.apache.hadoop.fs.Path;
    import org.apache.hadoop.io.LongWritable;
    import org.apache.hadoop.io.Text;
    import org.apache.hadoop.mapreduce.Job;
    import org.apache.hadoop.mapreduce.Mapper;
    import org.apache.hadoop.mapreduce.Reducer;
    import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
    import org.apache.hadoop.mapreduce.lib.input.KeyValueTextInputFormat;
    import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
    import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

    public class TopNMain 
    {
        public static class WordFreqComparator implements Comparator<WordFreq>
        {		
            // 2개의 WordFreq를 비교하여 결과값 리턴 
            public int compare(WordFreq a, WordFreq b)
            {
                if(a.getFreq() < b.getFreq()){ return -1; }			
                if(a.getFreq() > b.getFreq()){ return 1; }			
                return 0;			
            } // end of compare
        } // end of WordFreqComparator
        
        // Mapper class
        public static class Map extends Mapper<Text, Text, Text, LongWritable>
        {
            // (1) Map 만들기 *********************************************
            int topN = 10;
            Comparator<WordFreq> comparator = new WordFreqComparator();
            PriorityQueue<WordFreq> queue = new PriorityQueue<WordFreq>(topN, comparator);
            
            // 처음에 단 한번 불려짐
            protected void setup(Context context) throws IOException, InterruptedException
            {
                topN = context.getConfiguration().getInt("topN", topN);
            } // end of setup
            
            // 매번 잘라질때마다 불려짐
            public void map(Text key, Text value, Context context) throws IOException, InterruptedException
            {
                Long lValue = Long.parseLong(value.toString()); // 빈도수
                insert(queue, key.toString(), lValue, topN); // queue랑 key랑 빈도수랑 최대를 입력한다
            } // end of map
            
            // map() 메소드가 모두 호출된 후에 호출되는 메소드
            protected void cleanup(Context context) throws IOException, InterruptedException
            {
                while(queue.size() != 0 ) 
                {
                    WordFreq wordF = (WordFreq)queue.remove();
                    // wordF의 word와 freq를 형변환 해준다.
                    context.write(new Text(wordF.getWord()), new LongWritable(wordF.getFreq()));
                } // end of while
            } // end of cleanup
        } // end of Map
        
    /*
        Reducer class
        리듀스의 입력형식  :  Text, LongWritable (** 맵의 출력형식과 일치 )
        리듀스의 출력형식 :   Text, LongWritable 
    */
        public static class Reduce extends Reducer<Text, LongWritable, Text, LongWritable>
        {
            // (2) Reduce 만들기 *******************************************
            int topN = 10;
            Comparator<WordFreq> comparator = new WordFreqComparator();
            PriorityQueue<WordFreq> queue = new PriorityQueue<WordFreq>(topN, comparator);
            
            // 처음에 단 한번 불려짐
            protected void setup(Context context) throws IOException, InterruptedException
            {
                topN = context.getConfiguration().getInt("topN", topN);
            } // end of setup
            
            public void reduce(Text key, Iterable<LongWritable> value, Context context) throws IOException, InterruptedException
            {
                long sum = 0;
                for(LongWritable val : value)
                {
                    sum += val.get();
                } // end of for
                
                insert(queue, key.toString(), sum, topN);
            } // end of reduce
            
            // reduce() 메소드가 모두 호출된 후에 호출되는 메소드
            protected void cleanup(Context context) throws IOException, InterruptedException
            {
                while(queue.size() != 0 ) 
                {
                    WordFreq wordF = (WordFreq)queue.remove();
                    // wordF의 word와 freq를 형변환 해준다.
                    context.write(new Text(wordF.getWord()), new LongWritable(wordF.getFreq()));
                } // end of while
            } // end of cleanup
        } // end of Reduce
    /*
        인자 : 우선순위큐, 단어, 빈도수, 상위N개 
        N값 - 큐의 갯수 
    */
        public static void insert(PriorityQueue queue, String word, Long lValue, int topN)
        {	
            WordFreq miniWF = (WordFreq)queue.peek();
            // 우선순위큐는 지정한 준에 (빈도수)따라 순서대로 저장하고 있기에 
            // peek() 호출시 빈도수가 작은 (즉, 우선순위가 낮은) 원소가 출력된다. 
            
            // 큐의 갯수가  N개보다 작으면 큐에 추가
            // 큐의 갯수보다 큰 경우에서는 큐에서 우선순위가 낮은 원소의 빈도수보다 크면 큐에 추가 
            if(queue.size() < topN || miniWF.getFreq() < lValue )
            {
                WordFreq wordFreq = new WordFreq(word, lValue);
                queue.add(wordFreq);
            } // end of if		
            // 조건에 맞아서 큐에 넣은 경우  큐의 크기가 10개를 넘으면 
            // 우선순위 낮은 원소 삭제하여 큐의 갯수를 10개 유지한다.
            if(queue.size() > topN)
            {
                queue.remove();
            } // end of if
        } // end of insert
        
        public static void main(String[] args) throws Exception 
        {
            Configuration conf = new Configuration();
            Job job = Job.getInstance(conf, "TopNMain");
            
            job.setJarByClass(TopNMain.class);
            job.setMapperClass(Map.class);
            job.setReducerClass(Reduce.class);
            job.setNumReduceTasks(1); // 리듀스태스크 1개로 지정 		

            job.setOutputKeyClass(Text.class);
            job.setOutputValueClass(LongWritable.class);			
            
            job.setInputFormatClass(KeyValueTextInputFormat.class);
            job.setOutputFormatClass(TextOutputFormat.class);
            
            FileInputFormat.addInputPath(job, new Path(args[0]));
            FileOutputFormat.setOutputPath(job, new Path(args[1]));
            job.getConfiguration().setInt("topN", Integer.parseInt(args[2]));
            // 잡의 설정값 추가하여 Map과 Reduce 클래스에서 사용가능 
            
            job.waitForCompletion(true);
        } // end of main
    } // end of TopNMain
    ~~~
    2. WinCSP 업로드 후
    <br> 1) ls /home/hadoop/source
    <br> 2) yarn jar /home/hadoop/source/lab2.jar sample2class.TopNMain /output/wordcount2/part-r-00000 /output/topn1 10
    <br> 3) hdfs dfs -ls /output/topn1
    <br> 4) hdfs dfs -cat /output/topn1/part-r-00000

* CountTrigram
    1. sample2class.CountTrigram 생성
    ~~~java
    package sample2class;

    import java.io.IOException;
    import java.util.StringTokenizer;

    import org.apache.hadoop.conf.Configuration;
    import org.apache.hadoop.fs.Path;
    import org.apache.hadoop.io.IntWritable;
    import org.apache.hadoop.io.LongWritable;
    import org.apache.hadoop.io.Text;
    import org.apache.hadoop.mapreduce.Job;
    import org.apache.hadoop.mapreduce.Mapper;
    import org.apache.hadoop.mapreduce.Reducer;
    import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
    import org.apache.hadoop.mapreduce.lib.input.KeyValueTextInputFormat;
    import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
    import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

    public class CountTrigram 
    {
        public static class Map extends Mapper<Text, Text, Text, IntWritable>
        {
            private final static IntWritable one = new IntWritable(1);
            private Text trigram = new Text();
    /*		
            A B C D E --> (A B C), (B C D), (C D E) 추출후에 다시 
            B C D E F 에서  3개씩  묶는다
    */ 
            public void map(Text key, Text value, Context context) throws IOException, InterruptedException
            {
                String line = value.toString();
                StringTokenizer tokenizer = new StringTokenizer(line,"\t\r\n\f |,!#\"$.'%&=+-_^@`~:?<>(){}[];*/");
                // (1) 단어 3개씩 묶기
                if(tokenizer.countTokens() >= 3 )
                {
                    String firstToken = tokenizer.nextToken().toLowerCase();
                    String secondToken = tokenizer.nextToken().toLowerCase();
                    // 안녕하세요 여러분 우리는 좋은 사람들입니다
                    while(tokenizer.hasMoreTokens())
                    {
                        String thirdToken = tokenizer.nextToken().toLowerCase();
                        trigram.set(firstToken + " " + secondToken + " " + thirdToken);
                        context.write(trigram, one);
                        
                        firstToken = secondToken;
                        secondToken = thirdToken;
                    } // end of while
                } // end of if
            } // end of map
        } // end of Map
        
        // 리듀서 클래스 
        public static class Reduce extends Reducer<Text, IntWritable, Text, IntWritable>
        {
            public void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException
            {
                int sum = 0;
                for (IntWritable val : values)
                {
                    sum +=val.get();
                } // end of for
                context.write(key, new IntWritable(sum));
            } // end of reduce
        } // end of Reduce
        
        // 잡을 2개를 생성 - CountTrigram / TopNMain
        public static void main(String[] args) throws Exception 
        {
            Configuration conf1 = new Configuration();
            Job job1 = Job.getInstance(conf1, "Count Trigram");
            
            job1.setJarByClass(CountTrigram.class);
            job1.setMapperClass(Map.class);
            //job1.setCombinerClass(Reduce.class);
            job1.setReducerClass(Reduce.class);

            job1.setOutputKeyClass(Text.class);
            job1.setOutputValueClass(IntWritable.class); //***
            
            job1.setInputFormatClass(KeyValueTextInputFormat.class);
            job1.setOutputFormatClass(TextOutputFormat.class);
            
            FileInputFormat.addInputPath(job1, new Path(args[0]));
            FileOutputFormat.setOutputPath(job1, new Path(args[1]));

            if(!job1.waitForCompletion(true)) return;
            
            //--------------------------------------------------
            Configuration conf2 = new Configuration();
            Job job2 = Job.getInstance(conf2, "TopNMain");
            
            job2.setJarByClass(TopNMain.class);
            job2.setMapperClass(TopNMain.Map.class); 	 // # 클래스 
            job2.setReducerClass(TopNMain.Reduce.class); // # 클래스 
            job2.setNumReduceTasks(1);

            job2.setOutputKeyClass(Text.class);
            job2.setOutputValueClass(LongWritable.class);
            
            job2.setInputFormatClass(KeyValueTextInputFormat.class);
            job2.setOutputFormatClass(TextOutputFormat.class);
            
            // 위의 잡에서 출력된 내용을 입력으로 받아야 함 
            // 출력경로 :  입력경로 / topN 하위폴더 
            FileInputFormat.addInputPath(job2, new Path(args[1]));
            FileOutputFormat.setOutputPath(job2, new Path(args[1]+"//topN"));
            job2.getConfiguration().setInt("topN", 10);
            
            if(!job2.waitForCompletion(true)) return;
        } // end of main
    } // end of CountTrigram 
    ~~~
    2. WinCSP 업로드 후
    <br> 1) ls /home/hadoop/source
    <br> 2) yarn jar /home/hadoop/source/lab3.jar sample2class.CountTrigram /input/data/wiki/10K.ID.CONTENS /output/trigram1/part-r-00000
    <br> 3) hdfs dfs -ls /output/trigram1
    <br> 4) hdfs dfs -ls -R /output/trigram1
    <br> 5) hdfs dfs -cat /output/trigram1/part-r-00000 | head - 20
    <br> 6) hdfs dfs -cat /output/trigram1/topN/part-r-00000 | head - 20

## 정리
#!/usr/bin/perl

use strict;
use warnings FATAL => 'all';
use bytes;


my $wait_max = 100;

my $base = 2;
my $delta = 10;


my $cntr = 1;



my $url="curl -G \"https://api.github.com/search/repositories?q=language:python+forks:BEGIN+is:public+archived:false+pushed:>=2021-01-01&per_page=100&page=PAGE\"";
#curl -G "https://api.github.com/search/repositories?q=language:python+forks:1000..1500+is:public+archived:false+pushed:>=2021-01-01&per_page=100&page=2"

print "done\n";
my $begin = $base;
my $end = $base;
my $page_id=1;

foreach $i (10 .. 15){
$cntr ++;

my $rnd_sleep = int(rand($wait_max));

$begin = $i;
$end = $i; #begin+ $delta;

$nurl = $url;
$counter = $base;
  
$nurl =~ s/BEGIN/$i/g;
#$nurl =~ s/END/$end/g;
my $first_url=$nurl ;

$first_url  =~ s/PAGE/$page_id/g;

$base+=1;

my $name = "tmp-".$begin."_".$end.".1.json";
$target = "tmp-".$begin."_".$end.".1.json.gz";

print "$begin $end $target\n";
my $cmd=  $first_url ;#. " | gzip >" . $target;

print "\twait $rnd_sleep ==> $i $counter $target \n";
print "\t\t$cmd\n";

open (PIPE, "$cmd |") or die "Unable to pipe";
my @lines = <PIPE>;
close(PIPE);
$count  = 0;
foreach my $l (@lines){
  print $l;
  if ($l =~ /\"total_count\":\s*(\d+)/){
    $count = $1;
    last;
  }
}

open (FH, ">$name") or die "Unable to open $name\n";
print FH @lines ;
close(FH);
system("gzip $name");

sleep($rnd_sleep);

next if ($count < 100);

my $pages =int( ($count - 100)/100);
my $modulo = ($count - 100)%100;


if ($modulo >0){
  $tot_pages  = $pages + 1;
}
for my $p (2..(1+$tot_pages)){
 last if ($p>10);

  $rnd_sleep = int(rand($wait_max));
  print "\t\tLoading $p\n";
  $target = "tmp-".$begin."_".$end.".$p.json.gz";
  print "\t\tLoading $p ==> $target\n";
  my $next_url=$nurl ;

  $next_url  =~ s/PAGE/$p/g;
  
  $cmd=  $next_url . " | gzip >" . $target;
  print "$cmd\n";
  system("$cmd");
  sleep($rnd_sleep);
}

print "\tCount $count pages $pages modulo $modulo tot pages  $tot_pages\n";


$rnd_sleep = int(rand($wait_max));

}
exit(0);


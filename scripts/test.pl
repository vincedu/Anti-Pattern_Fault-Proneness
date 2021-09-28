#!/usr/bin/perl

use strict;
use warnings;

my $wait_max = 100;

my $base = 2;
my $delta = 10;


my $cntr = 1;


my $url="https://api.github.com/search/repositories?q=language:java+is:public+forks:0+topic:android+archived:false&per_page=100&page=PAGE";
#"curl -G \"https://api.github.com/search/repositories?q=language:python+forks:BEGIN+is:public+archived:false+pushed:>=2021-01-01&per_page=100&page=PAGE\"";
#curl -G "https://api.github.com/search/repositories?q=language:python+forks:1000..1500+is:public+archived:false+pushed:>=2021-01-01&per_page=100&page=2"
#curl -G "https://api.github.com/search/repositories?q=language:python+forks:10+stars:0..5+is:public+archived:false+pushed:>=2021-01-01&per_page=100&page=2"

print "done\n";
my $begin = $base;
my $end = $base;
my $page_id=1;


foreach my $i (13 .. 15){
    my $rnd_sleep = int(rand($wait_max));

    $begin = $i;
    $end = $i; #begin+ $delta;

    my $nurl = $url;
    my $counter = $base;

    $nurl =~ s/BEGIN/$i/g;
    #$nurl =~ s/END/$end/g;
    my $first_url=$nurl ;

    $first_url  =~ s/PAGE/$page_id/g;

    $base+=1;

    my $target = "tmp-".$begin."_".$end.".1.json.gz";

    print "$begin $end $target\n";
    my $cmd=  $first_url ;#. " | gzip >" . $target;

    print "\twait $rnd_sleep ==> $i $counter $target \n";
    print "\t\t$cmd\n";

    print "request to go find the total count \n";
    #downloading the project
    open (PIPE, "$cmd |") or die "Unable to pipe";
    my @lines = <PIPE>;
    close(PIPE);

    my $count  = 0;
    foreach my $l (@lines){
      print $l;
      if ($l =~ /\"total_count\":\s*(\d+)/){
          $l=~ s/[^0-9]//g;
          $count = int($l);
          last;
      }
    }

    my $j = 0;
    my $start = 0;
    my $stop = 5;
    $cmd = $url;

    print "request to go find sub project beginning \n";
    while ($j < $count) {
        my $count = 0;
        $cmd =~ s/BEGIN/$i+stars:$start..$stop/g;
        my $a = $cmd;
        $cmd  =~ s/PAGE/$page_id/g;
        print "\twait $rnd_sleep ==> $i $counter $target \n";
        print "\t\t$cmd\n";

        #downloading the project
        open(PIPE, "$cmd |") or die "Unable to pipe";
        my @lines = <PIPE>;
        close(PIPE);

        foreach my $l (@lines) {
            print $l;
            if ($l =~ /\"total_count\":\s*(\d+)/) {
                my $temp_l = $l;
                $temp_l =~ s/[^0-9]//g;
                $count = int($temp_l);
                $j += $count;
                last;
            }
        }
        my $name = "tmp-" . $i . "_" . $start . "_" . $stop . ".1.json";

        if ($count > 0) {
            open(FH, ">$name") or die "Unable to open $name\n";
            print FH @lines;
            close(FH);
            system("gzip $name");
        }

        sleep($rnd_sleep);

        if ($count > 100) {
            my $pages = int(($count - 100) / 100);
            my $modulo = ($count - 100) % 100;

            my $tot_pages = $pages;
            if ($modulo > 0) {
                $tot_pages = $pages + 1;
            }

            $cmd = $a;
            for my $p (2 .. (1 + $tot_pages)) {
                last if ($p > 10);

                $rnd_sleep = int(rand($wait_max));
                print "\t\tLoading $p\n";
                $target = "tmp-".$i."_".$start."_".$stop.".$p.json.gz";
                print "\t\tLoading $p ==> $target\n";

                # my $next_url=$nurl ;
                $cmd =~ s/PAGE/$p/g;
                $cmd = $cmd . " | gzip >" . $target;

                print "$cmd\n";
                system("$cmd");
                sleep($rnd_sleep);
                $cmd = $a;
            }
        }

        sleep($rnd_sleep);
        $start = $stop + 1;
        $stop += 5;
        $cmd = $url;
        last;
    }
    last;
}
exit(0);

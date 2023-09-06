cargo build --release
for file in $(ls *.cnf)
do
    echo "Querying file $file"
    expected=$(schlandals search -b min-in-degree -i $file)
    echo "Expected $expected"
    actual=$(schlandals approximate-search -b min-in-degree -i $file -e 0.0)
    echo "Actual $actual"
done